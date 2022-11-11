import os
from lionnetwork import start_app


"""
TODO:
1. fix job listing page, specifically drop-down menu
2. add payment feature
"""

if __name__ == '__main__':
    app = start_app()
    port = int(os.environ.get("PORT", 8111))
    app.run(debug=True, host="0.0.0.0", port=port)
