export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome to Lymeric Data Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Chemistry-aware data management for polymer research
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <h3 className="text-2xl font-bold text-gray-900 mb-3">📊 Materials Library</h3>
            <p className="text-gray-600 mb-4">
              Store and manage polymer materials with automatic SMILES canonicalization and feature extraction
            </p>
            <a href="/materials" className="text-blue-600 hover:text-blue-800 font-medium">
              Explore Materials →
            </a>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <h3 className="text-2xl font-bold text-gray-900 mb-3">🔬 ML Predictions</h3>
            <p className="text-gray-600 mb-4">
              Predict polymer properties (Tg, density, FFV) using our winning v85 Random Forest model
            </p>
            <a href="/predictions" className="text-blue-600 hover:text-blue-800 font-medium">
              Make Predictions →
            </a>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <h3 className="text-2xl font-bold text-gray-900 mb-3">🧪 Chemistry Features</h3>
            <p className="text-gray-600 mb-4">
              Automatic extraction of 21 chemistry features from SMILES using RDKit integration
            </p>
            <a href="#features" className="text-blue-600 hover:text-blue-800 font-medium">
              Learn More →
            </a>
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Platform Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600">21</div>
              <div className="text-gray-600 mt-2">Chemistry Features</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600">5</div>
              <div className="text-gray-600 mt-2">Polymer Properties</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600">v85</div>
              <div className="text-gray-600 mt-2">Winning Model</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600">0.075</div>
              <div className="text-gray-600 mt-2">Best Score (Private)</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
