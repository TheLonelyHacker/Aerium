"""
API Response Standardizer
Provides consistent response formatting across all API endpoints
"""

from flask import jsonify, make_response
from typing import Any, Dict, Optional, Tuple


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Dict, int]:
    """
    Create standardized success response
    
    Args:
        data: Response data payload
        message: Success message
        status_code: HTTP status code (default 200)
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
        'status_code': status_code
    }), status_code


def error_response(message: str, status_code: int = 400, error_code: str = None, details: Any = None) -> Tuple[Dict, int]:
    """
    Create standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code (default 400)
        error_code: Machine-readable error code
        details: Additional error details
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    response = {
        'success': False,
        'message': message,
        'status_code': status_code
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


def validation_error(field: str, message: str, value: Any = None) -> Tuple[Dict, int]:
    """
    Create validation error response
    
    Args:
        field: Field name that failed validation
        message: Validation error message
        value: The invalid value
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    details = {
        'field': field,
        'message': message
    }
    if value is not None:
        details['invalid_value'] = value
    
    return error_response(
        message=f"Validation error: {message}",
        status_code=422,
        error_code='VALIDATION_ERROR',
        details=details
    )


def not_found(resource_type: str = "Resource", resource_id: Any = None) -> Tuple[Dict, int]:
    """
    Create 404 not found response
    
    Args:
        resource_type: Type of resource (e.g., 'User', 'Sensor')
        resource_id: ID of the resource that wasn't found
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    message = f"{resource_type} not found"
    if resource_id is not None:
        message += f" (ID: {resource_id})"
    
    return error_response(
        message=message,
        status_code=404,
        error_code='NOT_FOUND'
    )


def unauthorized(reason: str = "Authentication required") -> Tuple[Dict, int]:
    """
    Create 401 unauthorized response
    
    Args:
        reason: Reason for rejection
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return error_response(
        message=reason,
        status_code=401,
        error_code='UNAUTHORIZED'
    )


def forbidden(reason: str = "Access denied") -> Tuple[Dict, int]:
    """
    Create 403 forbidden response
    
    Args:
        reason: Reason for rejection
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return error_response(
        message=reason,
        status_code=403,
        error_code='FORBIDDEN'
    )


def conflict(message: str = "Resource already exists", resource_type: str = None) -> Tuple[Dict, int]:
    """
    Create 409 conflict response
    
    Args:
        message: Conflict message
        resource_type: Type of resource in conflict
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return error_response(
        message=message,
        status_code=409,
        error_code='CONFLICT',
        details={'resource_type': resource_type} if resource_type else None
    )


def server_error(message: str = "An unexpected error occurred", error_details: str = None) -> Tuple[Dict, int]:
    """
    Create 500 server error response
    
    Args:
        message: Error message
        error_details: Technical error details (for logging)
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return error_response(
        message=message,
        status_code=500,
        error_code='SERVER_ERROR',
        details={'error_details': error_details} if error_details else None
    )


def created_response(data: Any = None, message: str = "Resource created successfully") -> Tuple[Dict, int]:
    """
    Create 201 created response
    
    Args:
        data: Created resource data
        message: Success message
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return success_response(data=data, message=message, status_code=201)


def no_content_response() -> Tuple[str, int]:
    """
    Create 204 no content response
    
    Returns:
        Tuple of (empty_string, 204)
    """
    return '', 204


def paginated_response(items: list, total: int, page: int, per_page: int, message: str = "Success") -> Tuple[Dict, int]:
    """
    Create paginated list response
    
    Args:
        items: List of items for this page
        total: Total number of items
        page: Current page number
        per_page: Items per page
        message: Success message
    
    Returns:
        Tuple of (response_dict, status_code) for Flask
    """
    return jsonify({
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        },
        'status_code': 200
    }), 200
