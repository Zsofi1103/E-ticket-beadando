from WebApp import db
from sqlalchemy import text


class Permission(db.Model):
    """Jogosultságok"""
    __tablename__ = 'permission'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)  # pl: "view_rooms", "manage_bookings"
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=text("UTC_TIMESTAMP()"), nullable=False)
    
    role_permissions = db.relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Permission {self.name}>"


class RolePermission(db.Model):
    """Role-jogosultság összerendelés"""
    __tablename__ = 'role_permission'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)  # pl: "guest", "receptionist", "admin"
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    
    permission = db.relationship('Permission', back_populates='role_permissions')
    
    def __repr__(self):
        return f"<RolePermission {self.role_name}: {self.permission.name}>"
