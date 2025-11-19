# Production-Ready Features - Future Implementation

**Document Date:** November 19, 2025  
**Status:** Deferred for production deployment

---

## Overview

This document outlines features and improvements that should be implemented before deploying the Lymeric Platform to production. The current implementation has basic functionality that works well for development and testing, but production deployment requires additional security, scalability, and user experience enhancements.

---

## 1. Advanced Security & Authentication

### Email Verification
**Priority:** HIGH  
**Effort:** 2-3 days

**Current State:**
- Users can register with any email address
- No email verification required
- Immediate access after registration

**Required Implementation:**
- Send verification email on registration
- Verification token with expiration (24 hours)
- Block login until email verified
- Resend verification email endpoint

**Technologies:**
- SendGrid/AWS SES for email delivery
- Email templates (HTML + plain text)
- Verification token generation (UUID + timestamp)

**Code Example:**
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_verification_email(user_email: str, token: str):
    message = Mail(
        from_email='noreply@lymeric.com',
        to_emails=user_email,
        subject='Verify your Lymeric account',
        html_content=f'<a href="https://app.lymeric.com/verify/{token}">Click to verify</a>'
    )
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg.send(message)
```

---

### Password Reset Flow
**Priority:** HIGH  
**Effort:** 1-2 days

**Current State:**
- No password reset mechanism
- Users locked out if they forget password
- Requires manual intervention

**Required Implementation:**
- "Forgot Password" link on login page
- Email password reset link with token
- Reset token expiration (1 hour)
- New password confirmation
- Password strength requirements

**Security Requirements:**
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, symbols
- Not in common password list
- Rate limiting on reset requests

---

### Role-Based Access Control (RBAC)
**Priority:** MEDIUM  
**Effort:** 3-4 days

**Current State:**
- Basic `is_admin` flag
- All users have same permissions
- No fine-grained access control

**Required Implementation:**
- Role hierarchy: Admin, Power User, Standard User, Read-Only
- Permission system:
  - `materials.create`, `materials.edit`, `materials.delete`
  - `training.start`, `training.view`
  - `admin.users`, `admin.system`
- Decorator-based endpoint protection
- Frontend role-based UI visibility

**Database Schema:**
```python
class Role(Base):
    id = Column(String(36), primary_key=True)
    name = Column(String(50))
    permissions = Column(JSON)  # List of permission strings

class UserRole(Base):
    user_id = Column(String(36), ForeignKey('users.id'))
    role_id = Column(String(36), ForeignKey('roles.id'))
```

---

### OAuth / Social Login
**Priority:** LOW  
**Effort:** 2-3 days

**Current State:**
- Email/password only
- Manual account creation

**Benefits:**
- Faster onboarding
- Improved user experience
- Reduced password management burden
- Higher conversion rates

**Providers to Support:**
- Google (highest priority for research users)
- GitHub (for developers)
- ORCID (for academic researchers)

**Libraries:**
- `authlib` for OAuth client
- Frontend OAuth buttons
- Account linking for existing users

---

## 2. Production Infrastructure

### Database Hardening
**Priority:** HIGH  
**Effort:** 2-3 days

**Current State:**
- Development database settings
- No connection pooling configuration
- Basic error handling

**Required Implementation:**
- **Connection Pooling:**
  ```python
  engine = create_engine(
      DATABASE_URL,
      pool_size=20,
      max_overflow=0,
      pool_pre_ping=True,
      pool_recycle=3600
  )
  ```
- **Backup Strategy:**
  - Automated daily backups to S3/Cloud Storage
  - Point-in-time recovery (every 5 minutes)
  - Backup retention: 30 days
  - Disaster recovery plan documented

- **Monitoring:**
  - Slow query logging
  - Connection pool metrics
  - Database size tracking
  - Alert on connection saturation

---

### Distributed Training
**Priority:** MEDIUM  
**Effort:** 4-5 days

**Current State:**
- Training runs in FastAPI background tasks
- Single-threaded execution
- No job queue

**Required Implementation:**
- **Celery Task Queue:**
  ```python
  from celery import Celery
  
  app = Celery('lymeric', broker='redis://localhost:6379')
  
  @app.task
  def train_model(config):
      # Long-running training job
      ...
  ```

- **Architecture:**
  - Redis as message broker
  - Celery workers on separate machines
  - Flower dashboard for job monitoring
  - Job priority queue
  - Result caching

- **Benefits:**
  - Multiple training jobs simultaneously
  - Horizontal scaling
  - No API timeout issues
  - Graceful shutdown

---

### Caching Layer
**Priority:** MEDIUM  
**Effort:** 2 days

**Current State:**
- No caching
- Every request hits database
- Slow repeated queries

**Required Implementation:**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@cache(expire=300)  # 5 minutes
async def get_materials():
    # Expensive query cached for 5 min
    ...
```

**Cache Strategy:**
- Materials list: 5 minutes
- Quality metrics: 15 minutes
- Predictions: 1 hour (hash SMILES as key)
- Correlations: 30 minutes
- User sessions: 24 hours

---

### Rate Limiting
**Priority:** HIGH (Production)  
**Effort:** 1 day

**Current State:**
- No rate limiting
- Vulnerable to abuse
- No API quota management

**Required Implementation:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/predictions")
@limiter.limit("10/minute")
async def predict(...):
    ...
```

**Rate Limits:**
- Predictions: 10/minute per user
- Training: 5/hour per user
- Upload: 10/hour per user
- Auth (login): 5/minute per IP

---

## 3. User Experience Improvements

### Design System (Figma)
**Priority:** MEDIUM  
**Effort:** 3-4 days

**Current State:**
- Tailwind CSS utility classes
- Inconsistent spacing and colors
- No formal design system

**Required Implementation:**
1. **Create Figma Design System:**
   - Color palette (primary, secondary, accent, neutrals)
   - Typography scale (headings, body, captions)
   - Component library (buttons, inputs, cards)
   - Spacing system (4px grid)
   - Icon set

2. **Design Key Flows:**
   - Onboarding wizard (3-step)
   - Material detail page
   - Training configuration
   - Dashboard layouts

3. **Accessibility:**
   - WCAG 2.1 AA compliance
   - Keyboard navigation
   - Screen reader support
   - Color contrast ratios

**Figma Benefits:**
- Faster design iteration
- Developer handoff with specs
- Consistent brand identity
- Stakeholder previews

---

### Progressive Web App (PWA)
**Priority:** LOW  
**Effort:** 2 days

**Benefits:**
- Offline support
- Install on mobile devices
- Push notifications
- Improved mobile UX

**Implementation:**
- Service worker for caching
- Web app manifest
- Offline fallback pages
- Background sync for uploads

---

### Advanced Visualizations
**Priority:** MEDIUM  
**Effort:** 3-4 days

**Additions:**
- **3D Molecular Viewer:** Three.js or Mol* for interactive 3D structures
- **Interactive Property Charts:** Plotly for zoom/pan
- **Heatmaps:** Property correlation heatmaps
- **Time Series:** Track property changes over datasets
- **Export Options:** SVG, PNG, PDF for charts

---

## 4. Data & ML Enhancements

### Substructure Highlighting
**Priority:** LOW  
**Effort:** 2 days

**Current State:**
- Search results show full molecule
- No visual indication of match

**Implementation:**
```python
from rdkit.Chem import Draw

def highlight_substructure(mol, query):
    match = mol.GetSubstructMatch(query)
    return Draw.MolToImage(mol, highlightAtoms=match)
```

---

### Model Versioning System
**Priority:** MEDIUM  
**Effort:** 2-3 days

**Current State:**
- Models overwrite each other
- No version history
- Can't rollback

**Implementation:**
- **Database Schema:**
  ```python
  class ModelVersion(Base):
      id = Column(String(36), primary_key=True)
      property = Column(String(50))
      version = Column(Integer)
      method = Column(String(50))  # basic, optuna, autogluon
      metrics = Column(JSON)
      model_path = Column(String(500))
      is_active = Column(Boolean)
      created_at = Column(DateTime)
  ```

- **Features:**
  - Semantic versioning (v1.0.0, v1.1.0, v2.0.0)
  - A/B testing (deploy 2 versions simultaneously)
  - Rollback to previous version
  - Performance comparison dashboard

---

### Dataset Versioning
**Priority:** MEDIUM  
**Effort:** 2 days

**Track:**
- When materials were added/modified
- Data lineage (imported from which CSV)
- Snapshot datasets for reproducibility
- Diff between dataset versions

---

## 5. Monitoring & Observability

### Application Performance Monitoring (APM)
**Priority:** HIGH (Production)  
**Effort:** 1-2 days

**Tools:**
- **Sentry** - Error tracking
- **DataDog/New Relic** - APM
- **Prometheus + Grafana** - Metrics

**Metrics to Track:**
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Database query performance
- ML prediction time
- Training job duration
- Memory usage

---

### Logging Infrastructure
**Priority:** HIGH (Production)  
**Effort:** 1 day

**Current State:**
- Print statements
- No structured logs
- No centralized logging

**Implementation:**
```python
import structlog

logger = structlog.get_logger()
logger.info("prediction_made", smiles=smiles, duration_ms=123)
```

**Log Aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- CloudWatch Logs (AWS)
- Google Cloud Logging (GCP)

**Log Levels:**
- DEBUG: Development only
- INFO: Normal operations
- WARNING: Degraded performance
- ERROR: Request failures
- CRITICAL: System down

---

## 6. Testing & Quality

### Automated Testing
**Priority:** HIGH  
**Effort:** 3-4 days

**Current Coverage:** ~30% (basic tests only)

**Required:**
- **Unit Tests:** 80%+ coverage
  - All service methods
  - Edge cases
  - Error handling
  
- **Integration Tests:**
  - Full API workflows
  - Database transactions
  - File uploads
  
- **E2E Tests (Playwright):**
  ```typescript
  test('user can register and predict', async ({ page }) => {
      await page.goto('/register');
      // ... register flow
      await page.goto('/predictions');
      // ... prediction flow
  });
  ```

---

### CI/CD Pipeline
**Priority:** HIGH (Production)  
**Effort:** 2 days

**GitHub Actions:**
```yaml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest
      - run: npm test
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh
```

**Stages:**
1. Lint (black, eslint)
2. Test (pytest, jest)
3. Build (Docker images)
4. Deploy (staging → production)

---

## Implementation Priority

### Phase 1: Security (Week 1-2)
1. Email verification
2. Password reset
3. Rate limiting
4. HTTPS enforcement

### Phase 2: Infrastructure (Week 3-4)
1. Database backups
2. APM/Logging
3. CI/CD pipeline
4. Caching layer

### Phase 3: UX (Week 5-6)
1. Figma design system
2. Design implementation
3. Advanced visualizations
4. Mobile responsiveness

### Phase 4: Scale (Week 7-8)
1. Distributed training (Celery)
2. Model versioning
3. RBAC
4. OAuth

---

## Cost Estimates

**Security & Auth:** $0 (code only)  
**Infrastructure:** $50-100/month (backups, monitoring)  
**Design:** $500-1000 (Figma + design time)  
**Total:** ~$1500 one-time + $75/month ongoing

---

## Conclusion

The current platform is **development-ready** but needs these enhancements for **production deployment**. Prioritize security and infrastructure first, then user experience and scaling features.

**Estimated Total Effort:** 6-8 weeks (1 developer full-time)

**Status:** ✅ Documented, ready for implementation
