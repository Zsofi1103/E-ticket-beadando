-- Hotel Booking System Tables

-- Room table
CREATE TABLE IF NOT EXISTS room (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venue_id INT,
    room_number VARCHAR(50) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    price_per_night DECIMAL(10, 2) NOT NULL,
    description TEXT,
    equipment VARCHAR(500),
    status ENUM('available', 'occupied', 'maintenance', 'unavailable') DEFAULT 'available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (venue_id) REFERENCES venue(id),
    INDEX idx_room_number (room_number),
    INDEX idx_venue_id (venue_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Booking table
CREATE TABLE IF NOT EXISTS booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in DATETIME NOT NULL,
    check_out DATETIME NOT NULL,
    guests_count INT NOT NULL,
    status ENUM('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled') DEFAULT 'pending',
    total_price DECIMAL(10, 2) DEFAULT 0,
    check_in_time DATETIME,
    check_out_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (room_id) REFERENCES room(id),
    INDEX idx_user_id (user_id),
    INDEX idx_room_id (room_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Extra Service table
CREATE TABLE IF NOT EXISTS extra_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Booking Service (N:N relationship)
CREATE TABLE IF NOT EXISTS booking_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    FOREIGN KEY (service_id) REFERENCES extra_service(id),
    INDEX idx_booking_id (booking_id),
    INDEX idx_service_id (service_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Invoice table
CREATE TABLE IF NOT EXISTS invoice (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    total_amount DECIMAL(10, 2) NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    INDEX idx_booking_id (booking_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Permission table
CREATE TABLE IF NOT EXISTS permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Role Permission table
CREATE TABLE IF NOT EXISTS role_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (permission_id) REFERENCES permission(id),
    INDEX idx_role_name (role_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Audit Log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    INDEX idx_user_id (user_id),
    INDEX idx_booking_id (booking_id),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Alter user table to add new fields and update role enum
ALTER TABLE user ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE user ADD COLUMN IF NOT EXISTS address VARCHAR(500);

-- Sample data: Extra Services
INSERT INTO extra_service (name, price, description) VALUES
('Pár extra párna', 2000, 'Kényelmes extra párnák'),
('Fürdőköpeny szett', 3000, 'Luxus fürdőköpeny szett'),
('Masszázs csomag', 15000, 'Relaxáló masszázs'),
('Mini bar feltöltés', 5000, 'Szobai mini bar feltöltése'),
('Szobaszervíz ebéd', 8000, 'Szobába szállított ebéd'),
('Airport transfer', 6000, 'Repülőtér-szálloda szállítás'),
('Late checkout', 4000, 'Későbbi ki- vagy bejelentkezés')
ON DUPLICATE KEY UPDATE name=name;

-- Sample data: Permissions
INSERT INTO permission (name, description) VALUES
('view_rooms', 'Szobák megtekintése'),
('book_room', 'Szoba foglalása'),
('view_bookings', 'Foglalások megtekintése'),
('manage_bookings', 'Foglalások kezelése'),
('manage_checkin', 'Check-in/Check-out kezelés'),
('manage_rooms', 'Szobakezelés'),
('manage_users', 'Felhasználókezelés'),
('view_invoices', 'Számlák megtekintése'),
('manage_services', 'Extra szolgáltatások kezelése'),
('view_audit_logs', 'Audit napló megtekintése')
ON DUPLICATE KEY UPDATE name=name;

-- Sample data: Role Permissions
-- Guest roles
INSERT INTO role_permission (role_name, permission_id) SELECT 'guest', id FROM permission WHERE name IN ('view_rooms', 'book_room', 'view_bookings', 'view_invoices')
ON DUPLICATE KEY UPDATE role_name=role_name;

-- Receptionist roles
INSERT INTO role_permission (role_name, permission_id) SELECT 'receptionist', id FROM permission WHERE name IN ('view_rooms', 'view_bookings', 'manage_bookings', 'manage_checkin', 'manage_services')
ON DUPLICATE KEY UPDATE role_name=role_name;

-- Manager roles (includes receptionist + admin features)
INSERT INTO role_permission (role_name, permission_id) SELECT 'manager', id FROM permission WHERE name IN ('view_rooms', 'manage_rooms', 'view_bookings', 'manage_bookings', 'manage_checkin', 'manage_users', 'manage_services', 'view_invoices', 'view_audit_logs')
ON DUPLICATE KEY UPDATE role_name=role_name;

-- Admin roles (all permissions)
INSERT INTO role_permission (role_name, permission_id) SELECT 'admin', id FROM permission
ON DUPLICATE KEY UPDATE role_name=role_name;

-- Sample Rooms
INSERT INTO room (room_number, capacity, price_per_night, description, equipment, status) VALUES
('101', 2, 35000, 'Kényelmes szoba két ágyon', 'TV, Internet, Klimatizálás, Fürdőszoba', 'available'),
('102', 2, 35000, 'Standard szoba', 'TV, Internet, Klimatizálás, Fürdőszoba', 'available'),
('201', 4, 55000, 'Családi szoba, konyha', 'TV, Internet, Klimatizálás, Konyha, Fürdőszoba', 'available'),
('202', 3, 48000, 'Deluxe szoba', 'TV, Internet, Klimatizálás, Minibar, Fürdőszoba', 'available'),
('301', 2, 45000, 'Premium szoba kilátással', 'TV, Internet, Klimatizálás, Balkon, Fürdőszoba', 'available'),
('302', 1, 25000, 'Egyszemélyes szoba', 'TV, Internet, Klimatizálás, Fürdőszoba', 'available')
ON DUPLICATE KEY UPDATE room_number=room_number;
