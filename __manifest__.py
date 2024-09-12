{
    "name": "Authenticate via HTTP Remote User",
    "version": "17.0.1.0.0",
    "category": "Administration",
    "summary": "Provide HTTP Remote User authentication for Odoo.",
    "development_status": "Production/Stable",
    "author": "Christopher Piggott",
    "maintainer": "Christopher Piggott",
    "website": "https://www.rit.edu/gis",
    "depends": ["base", "web", "base_setup"],
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "data": [
        # Paths to XML files, security rules, etc.
    ],
    "external_dependencies": {
        "python": [],  # List of required Python libraries, e.g., ["requests"]
        "bin": []  # List of required executable tools, e.g., ["curl"]
    }
}
