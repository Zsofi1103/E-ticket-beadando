"""
OpenAPI/Swagger Configuration for Event-Ticket + Hotel Booking System
"""

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

api_info = {
    "title": "Event-Ticket + Hotel Booking API",
    "version": "1.0.0",
    "description": "REST API for Event management and Hotel room booking system",
    "contact": {
        "name": "API Support",
        "url": "http://localhost:5000"
    },
    "license": {
        "name": "MIT License"
    }
}

# API Endpoint Specs
EVENT_ENDPOINTS = {
    "GET /api/events": {
        "summary": "List all events",
        "description": "Retrieve all events with optional pagination and filtering",
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 1
            },
            {
                "name": "category_id",
                "in": "query",
                "type": "integer",
                "required": False
            }
        ],
        "responses": {
            "200": {
                "description": "List of events",
                "schema": {
                    "type": "object",
                    "properties": {
                        "events": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "price": {"type": "number"},
                                    "start_at": {"type": "string", "format": "datetime"},
                                    "categories": {"type": "array"},
                                    "venue": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

BOOKING_ENDPOINTS = {
    "POST /guest/book/<room_id>": {
        "summary": "Create new room booking",
        "description": "Book a hotel room for specified dates",
        "parameters": [
            {
                "name": "room_id",
                "in": "path",
                "type": "integer",
                "required": True
            },
            {
                "name": "check_in",
                "in": "formData",
                "type": "string",
                "format": "date",
                "required": True
            },
            {
                "name": "check_out",
                "in": "formData",
                "type": "string",
                "format": "date",
                "required": True
            },
            {
                "name": "guests_count",
                "in": "formData",
                "type": "integer",
                "required": True
            }
        ],
        "responses": {
            "200": {"description": "Booking created successfully"},
            "400": {"description": "Validation error"},
            "404": {"description": "Room not found"},
            "409": {"description": "Room not available for dates"}
        }
    },
    
    "GET /guest/bookings": {
        "summary": "Get user's bookings",
        "description": "Retrieve all bookings for the logged-in user",
        "responses": {
            "200": {
                "description": "List of user's bookings",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "room": {"type": "object"},
                            "check_in": {"type": "string", "format": "datetime"},
                            "check_out": {"type": "string", "format": "datetime"},
                            "status": {"type": "string", "enum": ["pending", "confirmed", "checked_in", "checked_out", "cancelled"]},
                            "total_price": {"type": "number"}
                        }
                    }
                }
            },
            "401": {"description": "Not authenticated"}
        }
    },
    
    "GET /guest/booking/<booking_id>": {
        "summary": "Get booking details",
        "description": "Retrieve detailed information for a specific booking",
        "parameters": [
            {
                "name": "booking_id",
                "in": "path",
                "type": "integer",
                "required": True
            }
        ],
        "responses": {
            "200": {"description": "Booking details"},
            "404": {"description": "Booking not found"},
            "403": {"description": "Access denied"}
        }
    }
}

ADMIN_ENDPOINTS = {
    "GET /admin/rooms": {
        "summary": "List all rooms (admin only)",
        "description": "Retrieve all hotel rooms with pagination",
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "default": 1
            }
        ],
        "responses": {
            "200": {"description": "List of rooms"},
            "403": {"description": "Admin access required"}
        }
    },
    
    "POST /admin/rooms/new": {
        "summary": "Create new room (admin only)",
        "description": "Add a new hotel room to the system",
        "parameters": [
            {
                "name": "room_number",
                "in": "formData",
                "type": "string",
                "required": True
            },
            {
                "name": "capacity",
                "in": "formData",
                "type": "integer",
                "required": True
            },
            {
                "name": "price_per_night",
                "in": "formData",
                "type": "number",
                "required": True
            },
            {
                "name": "venue_id",
                "in": "formData",
                "type": "integer"
            }
        ],
        "responses": {
            "200": {"description": "Room created"},
            "400": {"description": "Validation error"},
            "403": {"description": "Admin access required"}
        }
    },
    
    "PUT /admin/rooms/<room_id>/edit": {
        "summary": "Update room (admin only)",
        "description": "Modify hotel room details",
        "parameters": [
            {
                "name": "room_id",
                "in": "path",
                "type": "integer",
                "required": True
            }
        ],
        "responses": {
            "200": {"description": "Room updated"},
            "404": {"description": "Room not found"},
            "403": {"description": "Admin access required"}
        }
    },
    
    "DELETE /admin/rooms/<room_id>/delete": {
        "summary": "Delete room (admin only)",
        "description": "Remove a hotel room from the system",
        "parameters": [
            {
                "name": "room_id",
                "in": "path",
                "type": "integer",
                "required": True
            }
        ],
        "responses": {
            "200": {"description": "Room deleted"},
            "404": {"description": "Room not found"},
            "409": {"description": "Room has active bookings"},
            "403": {"description": "Admin access required"}
        }
    }
}

# Authentication Scheme
SECURITY_SCHEMES = {
    "Bearer": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "JWT Token (Bearer scheme) or Session Cookie"
    }
}

# Data Models for Schema
MODELS = {
    "User": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "phone": {"type": "string"},
            "address": {"type": "string"},
            "role": {"type": "string", "enum": ["guest", "receptionist", "manager", "admin"]},
            "created_at": {"type": "string", "format": "datetime"}
        }
    },
    "Event": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "price": {"type": "number"},
            "start_at": {"type": "string", "format": "datetime"},
            "venue": {"$ref": "#/definitions/Venue"},
            "categories": {"type": "array", "items": {"type": "object"}},
            "created_at": {"type": "string", "format": "datetime"}
        }
    },
    "Room": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "room_number": {"type": "string"},
            "capacity": {"type": "integer"},
            "price_per_night": {"type": "number"},
            "description": {"type": "string"},
            "equipment": {"type": "string"},
            "status": {"type": "string", "enum": ["available", "occupied", "maintenance", "unavailable"]},
            "venue": {"$ref": "#/definitions/Venue"},
            "created_at": {"type": "string", "format": "datetime"}
        }
    },
    "Booking": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "user": {"$ref": "#/definitions/User"},
            "room": {"$ref": "#/definitions/Room"},
            "check_in": {"type": "string", "format": "datetime"},
            "check_out": {"type": "string", "format": "datetime"},
            "guests_count": {"type": "integer"},
            "status": {"type": "string", "enum": ["pending", "confirmed", "checked_in", "checked_out", "cancelled"]},
            "total_price": {"type": "number"},
            "created_at": {"type": "string", "format": "datetime"}
        }
    },
    "Venue": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "address": {"type": "string"},
            "capacity": {"type": "integer"}
        }
    }
}

API_TAGS = {
    "Events": "Event management endpoints",
    "Bookings": "Hotel room booking endpoints",
    "Administration": "Admin-only management endpoints",
    "Authentication": "User authentication endpoints",
    "Profiles": "User profile management endpoints"
}
