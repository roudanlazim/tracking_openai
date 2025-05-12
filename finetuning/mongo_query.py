# query_config.py

query = {
    "$expr": {
        "$regexMatch": {
            "input": { "$arrayElemAt": ["$scans.scan", -1] },
            "regex": "^request$",
            "options": "i"
        }
    }
}