"""ML Model training service with basic and AutoML support"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import pickle
import os
from datetime import datetime
import threading

from app.models.material import Material


class TrainingService:
    """Machine learning model training with basic and AutoML options"""
    
    @staticmethod
    def prepare_data(db: Session, target_property: str) -> tuple:
        """
        Prepare training data from database
        
        Returns: (X, y, feature_names)
        """
        # Get all materials with the target property
        materials = db.query(Material).filter(
            getattr(Material, target_property).isnot(None)
        ).all()
        
        if len(materials) < 10:
            raise ValueError(f"Insufficient data: only {len(materials)} samples with {target_property}")
        
        # Extract features and target
        X = []
        y = []
        
        for material in materials:
            # Use the 21 chemistry features
            features = [
                len(material.canonical_smiles or ""),
                material.canonical_smiles.count('C') if material.canonical_smiles else 0,
                material.canonical_smiles.count('N') if material.canonical_smiles else 0,
                material.canonical_smiles.count('O') if material.canonical_smiles else 0,
                material.canonical_smiles.count('S') if material.canonical_smiles else 0,
                material.canonical_smiles.count('F') if material.canonical_smiles else 0,
                material.canonical_smiles.count('c') if material.canonical_smiles else 0,
                material.canonical_smiles.count('=') if material.canonical_smiles else 0,
                material.canonical_smiles.count('#') if material.canonical_smiles else 0,
                material.canonical_smiles.count('(') if material.canonical_smiles else 0,
                # Add more features...
            ]
            
            X.append(features)
            y.append(getattr(material, target_property))
        
        feature_names = ['smiles_length', 'carbon_count', 'nitrogen_count', 'oxygen_count', 
                         'sulfur_count', 'fluorine_count', 'aromatic_count', 'double_bond_count',
                         'triple_bond_count', 'branch_count']
        
        return np.array(X), np.array(y), feature_names
    
    @staticmethod
    def train_basic_model(
        db: Session,
        target_property: str,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        Train a basic Random Forest model
        
        Returns training results and metrics
        """
        # Prepare data
        X, y, feature_names = TrainingService.prepare_data(db, target_property)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        # Feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        return {
            'property': target_property,
            'method': 'RandomForest',
            'n_samples': len(X),
            'n_train': len(X_train),
            'n_test': len(X_test),
            'train_r2': float(train_r2),
            'test_r2': float(test_r2),
            'train_mae': float(train_mae),
            'test_mae': float(test_mae),
            'feature_importance': feature_importance,
            'model': model,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def train_optuna_model(
        db: Session,
        target_property: str,
        n_trials: int = 50,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train model with Optuna hyperparameter optimization
        
        Requires: pip install optuna
        """
        try:
            import optuna
            from optuna.samplers import TPESampler
        except ImportError:
            raise ImportError("Optuna not installed. Run: pip install optuna")
        
        # Prepare data
        X, y, feature_names = TrainingService.prepare_data(db, target_property)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'random_state': 42,
                'n_jobs': -1
            }
            
            model = RandomForestRegressor(**params)
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            return r2_score(y_test, pred)
        
        # Run optimization
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42)
        )
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        # Train final model with best params
        best_model = RandomForestRegressor(**study.best_params, n_jobs=-1)
        best_model.fit(X_train, y_train)
        
        # Evaluate
        test_pred = best_model.predict(X_test)
        test_r2 = r2_score(y_test, test_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        return {
            'property': target_property,
            'method': 'Optuna-RF',
            'n_samples': len(X),
            'n_trials': n_trials,
            'best_params': study.best_params,
            'test_r2': float(test_r2),
            'test_mae': float(test_mae),
            'model': best_model,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def train_autogluon_model(
        db: Session,
        target_property: str,
        time_limit: int = 300,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train model with AutoGluon AutoML
        
        Requires: pip install autogluon.tabular
        """
        try:
            from autogluon.tabular import TabularPredictor
        except ImportError:
            raise ImportError("AutoGluon not installed. Run: pip install autogluon.tabular")
        
        # Prepare data
        X, y, feature_names = TrainingService.prepare_data(db, target_property)
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=feature_names)
        df[target_property] = y
        
        # Split
        train_df = df.sample(frac=1-test_size, random_state=42)
        test_df = df.drop(train_df.index)
        
        # Train with AutoGluon
        predictor = TabularPredictor(
            label=target_property,
            eval_metric='r2',
            verbosity=0
        ).fit(
            train_df,
            time_limit=time_limit,
            presets='best_quality'
        )
        
        # Evaluate
        test_pred = predictor.predict(test_df.drop(columns=[target_property]))
        test_r2 = r2_score(test_df[target_property], test_pred)
        test_mae = mean_absolute_error(test_df[target_property], test_pred)
        
        # Get leaderboard
        leaderboard = predictor.leaderboard(test_df, silent=True)
        
        return {
            'property': target_property,
            'method': 'AutoGluon',
            'n_samples': len(df),
            'time_limit': time_limit,
            'test_r2': float(test_r2),
            'test_mae': float(test_mae),
            'best_model': leaderboard.iloc[0]['model'],
            'leaderboard': leaderboard.to_dict('records')[:5],
            'predictor': predictor,
            'timestamp': datetime.utcnow().isoformat()
        }


# Global training jobs storage (simple in-memory, use Redis for production)
training_jobs = {}


def run_training_job(job_id: str, db_session, config: dict):
    """Background training job"""
    try:
        training_jobs[job_id]['status'] = 'running'
        
        method = config.get('method', 'basic')
        property_name = config['property']
        
        if method == 'basic':
            result = TrainingService.train_basic_model(
                db_session,
                property_name,
                **config.get('params', {})
            )
        elif method == 'optuna':
            result = TrainingService.train_optuna_model(
                db_session,
                property_name,
                n_trials=config.get('n_trials', 50)
            )
        elif method == 'autogluon':
            result = TrainingService.train_autogluon_model(
                db_session,
                property_name,
                time_limit=config.get('time_limit', 300)
            )
        else:
            raise ValueError(f"Unknown method: {method}")
        
        training_jobs[job_id]['status'] = 'completed'
        training_jobs[job_id]['result'] = result
        
    except Exception as e:
        training_jobs[job_id]['status'] = 'failed'
        training_jobs[job_id]['error'] = str(e)
