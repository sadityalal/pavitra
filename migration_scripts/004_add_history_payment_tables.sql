-- =============================================
-- Migration: Add Missing History & Payment Tables
-- Fixed ENUM default values for MySQL compatibility
-- =============================================

USE pavitra;

-- =============================================
-- 1. PASSWORD HISTORY TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS password_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- =============================================
-- 2. PAYMENT METHODS TABLE (Indian Payment Support)
-- =============================================
CREATE TABLE IF NOT EXISTS payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    -- Payment method type for Indian market
    method_type ENUM('upi', 'card', 'netbanking', 'wallet', 'cash_on_delivery') NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- UPI specific fields
    upi_id VARCHAR(255),
    upi_app VARCHAR(100),  -- Google Pay, PhonePe, PayTM, etc.

    -- Card specific fields
    card_last_four VARCHAR(4),
    card_type VARCHAR(50),  -- visa, mastercard, rupay
    card_network VARCHAR(100),
    expiry_month INT,
    expiry_year INT,
    card_holder_name VARCHAR(255),

    -- Net Banking fields
    bank_name VARCHAR(255),
    account_last_four VARCHAR(4),

    -- Wallet fields
    wallet_provider VARCHAR(100),  -- PayTM, Amazon Pay, etc.
    wallet_id VARCHAR(255),

    -- Security
    token VARCHAR(500),  -- For payment gateway tokens

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_user_id (user_id),
    INDEX idx_method_type (method_type),
    INDEX idx_is_default (is_default)
);

-- =============================================
-- 3. PAYMENT TRANSACTIONS TABLE (Fixed ENUM defaults)
-- =============================================
CREATE TABLE IF NOT EXISTS payment_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    order_id INT NOT NULL,
    user_id INT NOT NULL,

    -- Payment details (INR)
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(50) NOT NULL,

    -- Payment gateway info for Indian providers
    gateway_name VARCHAR(100),  -- razorpay, paytm, etc.
    gateway_transaction_id VARCHAR(255),
    gateway_order_id VARCHAR(255),

    -- UPI specific
    upi_id VARCHAR(255),
    upi_transaction_id VARCHAR(255),
    vpa VARCHAR(255),  -- Virtual Payment Address

    -- Card specific
    card_last_four VARCHAR(4),
    card_type VARCHAR(50),
    card_network VARCHAR(100),

    -- Net Banking specific
    bank_name VARCHAR(255),
    bank_transaction_id VARCHAR(255),

    -- Wallet specific
    wallet_provider VARCHAR(100),
    wallet_transaction_id VARCHAR(255),

    -- Status and timing - FIXED ENUM DEFAULTS
    status ENUM('pending', 'processing', 'completed', 'failed', 'refunded') NOT NULL DEFAULT 'pending',
    payment_status ENUM('pending', 'authorized', 'captured', 'failed') NOT NULL DEFAULT 'pending',
    failure_reason TEXT,

    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    authorized_at TIMESTAMP NULL,
    captured_at TIMESTAMP NULL,
    failed_at TIMESTAMP NULL,
    refunded_at TIMESTAMP NULL,

    -- Refund info
    refund_amount DECIMAL(12,2) DEFAULT 0,
    refund_reason TEXT,

    -- Security
    signature TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_payment_method (payment_method)
);

-- =============================================
-- 4. ORDER HISTORY TABLE (Audit Trail)
-- =============================================
CREATE TABLE IF NOT EXISTS order_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,

    -- What changed
    field_changed VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,

    -- Who made the change
    changed_by INT NULL,
    change_type ENUM('system', 'admin', 'customer') NOT NULL DEFAULT 'system',

    -- Context
    reason TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_order_id (order_id),
    INDEX idx_created_at (created_at)
);

-- =============================================
-- VERIFICATION QUERY
-- =============================================
SELECT 'Migration completed successfully!' AS '';
SELECT CONCAT('Previous table count: 26') AS '';
SELECT CONCAT('New table count: ', COUNT(*)) FROM information_schema.tables
WHERE table_schema = 'pavitra';
SELECT '' AS '';
SELECT 'New tables added:' AS '';
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'pavitra'
AND table_name IN ('password_history', 'payment_methods', 'payment_transactions', 'order_history');