package main

import (
	"time"
	"gorm.io/gorm"
)

// User represents a user in the system
type User struct {
	ID         uint           `gorm:"primarykey" json:"id"`
	CreatedAt  time.Time      `json:"created_at"`
	UpdatedAt  time.Time      `json:"updated_at"`
	DeletedAt  gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
	Username   string         `gorm:"uniqueIndex;not null;size:100" json:"username"`
	Password   string         `gorm:"not null;size:255" json:"-"` // "-" tag untuk tidak menampilkan password di JSON
	
	// Relasi: User has many Categories
	Categories []Category `gorm:"foreignKey:UserID" json:"categories,omitempty"`
	
	// Relasi: User has many Transactions
	Transactions []Transaction `gorm:"foreignKey:UserID" json:"transactions,omitempty"`
}

// Category represents a transaction category
type Category struct {
	ID         uint           `gorm:"primarykey" json:"id"`
	CreatedAt  time.Time      `json:"created_at"`
	UpdatedAt  time.Time      `json:"updated_at"`
	DeletedAt  gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
	Name       string         `gorm:"not null;size:100" json:"name"`
	UserID     uint           `gorm:"not null;index" json:"user_id"`
	
	// Relasi: Category belongs to User
	User User `gorm:"foreignKey:UserID" json:"user,omitempty"`
	
	// Relasi: Category has many Transactions
	Transactions []Transaction `gorm:"foreignKey:CategoryID" json:"transactions,omitempty"`
}

// Transaction represents a financial transaction
type Transaction struct {
	ID              uint           `gorm:"primarykey" json:"id"`
	CreatedAt       time.Time      `json:"created_at"`
	UpdatedAt       time.Time      `json:"updated_at"`
	DeletedAt       gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
	Description     string         `gorm:"not null;size:255" json:"description"`
	Amount          float64        `gorm:"not null;type:decimal(10,2)" json:"amount"`
	TransactionDate time.Time      `gorm:"not null" json:"transaction_date"`
	UserID          uint           `gorm:"not null;index" json:"user_id"`
	CategoryID      *uint          `gorm:"index" json:"category_id"` // Nullable, bisa tidak ada kategori
	
	// Relasi: Transaction belongs to User
	User User `gorm:"foreignKey:UserID" json:"user,omitempty"`
	
	// Relasi: Transaction belongs to Category (optional)
	Category *Category `gorm:"foreignKey:CategoryID" json:"category,omitempty"`
}

// TableName methods untuk custom table names (opsional)
func (User) TableName() string {
	return "users"
}

func (Category) TableName() string {
	return "categories"
}

func (Transaction) TableName() string {
	return "transactions"
}