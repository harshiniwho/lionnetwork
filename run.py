import os

from lionnetwork import app

port = int(os.environ.get("PORT", 8111))
app.run(debug=True, host="0.0.0.0", port=port)
