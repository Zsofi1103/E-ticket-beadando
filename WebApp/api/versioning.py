"""
API Versioning Strategy Document
Defines how API versions are managed and evolved
"""

API_VERSIONS = {
    "v1": {
        "status": "current",
        "release_date": "2026-01-01",
        "description": "Initial API version",
        "endpoints": [
            "GET /api/v1/events",
            "GET /api/v1/rooms",
            "POST /api/v1/bookings",
        ]
    },
    "v2": {
        "status": "planning",
        "planned_release": "2026-06-01",
        "description": "Enhanced API with filtering, sorting",
        "changes": [
            "Advanced filtering (date range, price range)",
            "Sorting capabilities",
            "GraphQL endpoint",
            "Webhooks for real-time updates"
        ]
    }
}

# Current stable version
CURRENT_API_VERSION = "v1"

# Supported versions (backwards compatibility window)
SUPPORTED_VERSIONS = ["v1"]

# Deprecated versions (still work but with warnings)
DEPRECATED_VERSIONS = []

# Removed versions (no longer supported)
REMOVED_VERSIONS = []

"""
API VERSIONING STRATEGY

1. URL-based versioning (Recommended)
   /api/v1/events
   /api/v2/events

2. Header-based versioning (Alternative)
   Header: X-API-Version: 1.0
   GET /api/events

3. Query parameter versioning (Not recommended)
   /api/events?version=1

CHOSEN APPROACH: URL-based versioning
- Clear and explicit
- Easy to document
- Easy to implement in code
- Support multiple versions simultaneously
"""

VERSIONING_IMPLEMENTATION = {
    "strategy": "URL-based",
    "pattern": "/api/{version}/{resource}",
    "example": "/api/v1/bookings",
    "deprecation_path": "/api/v2/bookings (new endpoints)"
}

# Backwards compatibility rules
COMPATIBILITY_RULES = {
    "v1": {
        "endpoints": {
            "GET /api/v1/events": {
                "description": "List all events",
                "stability": "stable",
                "deprecated": False
            },
            "GET /api/v1/rooms": {
                "description": "List all rooms",
                "stability": "stable",
                "deprecated": False
            },
            "POST /api/v1/bookings": {
                "description": "Create new booking",
                "stability": "stable",
                "deprecated": False
            }
        },
        "breaking_changes_allowed": False,
        "support_until": "2026-12-31"
    },
    "v2": {
        "endpoints": {
            "GET /api/v2/events": {
                "description": "List events with advanced filters",
                "stability": "beta",
                "deprecated": False,
                "enhancements": ["filtering", "sorting", "pagination"]
            }
        },
        "breaking_changes": [
            "Response schema improvements",
            "Additional query parameters"
        ],
        "migration_guide": "See MIGRATION.md",
        "support_until": "2027-12-31"
    }
}

# Response format for versioned APIs
API_RESPONSE_FORMAT = {
    "v1": {
        "structure": {
            "status": "string",
            "data": "object | array",
            "error": "string (optional)",
            "timestamp": "ISO8601"
        },
        "example": {
            "status": "success",
            "data": [
                {
                    "id": 1,
                    "title": "Event Title",
                    "created_at": "2026-01-15T10:30:00Z"
                }
            ],
            "timestamp": "2026-05-17T14:20:00Z"
        }
    },
    "v2": {
        "structure": {
            "success": "boolean",
            "data": "object | array",
            "error": "object (optional)",
            "meta": {
                "pagination": "object",
                "timestamp": "ISO8601"
            }
        },
        "example": {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "title": "Event Title",
                    "venue": {
                        "id": 1,
                        "name": "Venue Name"
                    },
                    "created_at": "2026-01-15T10:30:00Z"
                }
            ],
            "meta": {
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total": 50
                },
                "timestamp": "2026-05-17T14:20:00Z"
            }
        }
    }
}

# Deprecation schedule
DEPRECATION_SCHEDULE = {
    "v1.0": {
        "deprecation_date": "2026-12-01",
        "removal_date": "2027-01-01",
        "replacement": "v2.0",
        "migration_steps": [
            "Update API calls to use /api/v2/ endpoints",
            "Review response format changes",
            "Update error handling",
            "Test thoroughly in staging"
        ]
    }
}

# Version-specific error codes
ERROR_CODES = {
    "v1": {
        "400": "Bad Request",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "Not Found",
        "409": "Conflict (e.g., booking overlap)",
        "500": "Internal Server Error",
        "503": "Service Unavailable"
    },
    "v2": {
        "400": "Bad Request",
        "401": "Unauthorized (include auth_error_code)",
        "403": "Forbidden (include permission_error_code)",
        "404": "Not Found",
        "409": "Conflict (detailed reason)",
        "422": "Unprocessable Entity (validation errors)",
        "429": "Too Many Requests (rate limit)",
        "500": "Internal Server Error",
        "503": "Service Unavailable"
    }
}

# Version HTTP headers
VERSION_HEADERS = {
    "request": {
        "Accept-Version": "1.0",  # Optional - client can specify
        "X-API-Version": "1.0"    # Optional alternative
    },
    "response": {
        "API-Version": "1.0",
        "X-API-Version": "1.0",
        "Deprecation": "false",   # true if deprecated
        "Sunset": "Sun, 31 Dec 2026 23:59:59 GMT"  # When version ends
    }
}

# Rate limiting by version
RATE_LIMITS = {
    "v1": {
        "requests_per_minute": 60,
        "requests_per_hour": 3600,
        "authenticated": True
    },
    "v2": {
        "requests_per_minute": 100,
        "requests_per_hour": 6000,
        "authenticated": True
    }
}

# Documentation versioning
DOCUMENTATION = {
    "v1": {
        "url": "/api/v1/docs",
        "openapi": "/api/v1/openapi.json",
        "postman_collection": "/docs/postman-v1.json"
    },
    "v2": {
        "url": "/api/v2/docs",
        "openapi": "/api/v2/openapi.json",
        "postman_collection": "/docs/postman-v2.json"
    }
}
