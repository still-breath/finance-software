package main

import (
	"fmt"
	"log"
	"os"
	
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// ConnectDatabase menghubungkan ke database PostgreSQL menggunakan GORM
func ConnectDatabase() error {
	// Membaca DSN dari environment variable
	dsn := os.Getenv("DATABASE_DSN")
	if dsn == "" {
		// Fallback DSN jika environment variable tidak tersedia
		host := getEnv("DB_HOST", "localhost")
		port := getEnv("DB_PORT", "5432")
		user := getEnv("DB_USER", "postgres")
		password := getEnv("DB_PASSWORD", "123123")
		dbname := getEnv("DB_NAME", "finance_db")
		sslmode := getEnv("DB_SSLMODE", "disable")
		timezone := getEnv("DB_TIMEZONE", "Asia/Jakarta")
		
		dsn = fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=%s TimeZone=%s",
			host, user, password, dbname, port, sslmode, timezone)
	}
	
	// Konfigurasi GORM
	config := &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	}
	
	// Membuka koneksi ke database
	var err error
	DB, err = gorm.Open(postgres.Open(dsn), config)
	if err != nil {
		return fmt.Errorf("failed to connect to database: %w", err)
	}
	
	// Konfigurasi connection pool
	sqlDB, err := DB.DB()
	if err != nil {
		return fmt.Errorf("failed to get database instance: %w", err)
	}
	
	// Set maksimum jumlah koneksi idle
	sqlDB.SetMaxIdleConns(10)
	// Set maksimum jumlah koneksi terbuka
	sqlDB.SetMaxOpenConns(100)
	// Set maksimum waktu hidup koneksi
	// sqlDB.SetConnMaxLifetime(time.Hour)
	
	log.Println("Database connected successfully!")
	return nil
}

// RunMigrations menjalankan auto-migration untuk semua model
func RunMigrations() error {
	log.Println("Running database migrations...")
	
	err := DB.AutoMigrate(
		&User{},
		&Category{},
		&Transaction{},
	)
	
	if err != nil {
		return fmt.Errorf("failed to run migrations: %w", err)
	}
	
	log.Println("Database migrations completed successfully!")
	return nil
}

// CreateDefaultCategories membuat kategori default untuk sistem
func CreateDefaultCategories() error {
	log.Println("Creating default categories...")
	
	defaultCategories := []string{
		"Makanan & Minuman",
		"Transportasi",
		"Tagihan",
		"Belanja",
		"Hiburan",
		"Kesehatan",
		"Pendidikan",
		"Investasi",
		"Lainnya",
	}
	
	for _, categoryName := range defaultCategories {
		var existingCategory Category
		if err := DB.Where("name = ? AND user_id IS NULL", categoryName).First(&existingCategory).Error; err == gorm.ErrRecordNotFound {
			// Kategori belum ada, buat yang baru
			category := Category{
				Name: categoryName,
				// UserID: 0, // Kategori sistem/global
			}
			if err := DB.Create(&category).Error; err != nil {
				log.Printf("Failed to create default category '%s': %v", categoryName, err)
			}
		}
	}
	
	log.Println("Default categories created successfully!")
	return nil
}

// CloseDatabase menutup koneksi database
func CloseDatabase() error {
	if DB != nil {
		sqlDB, err := DB.DB()
		if err != nil {
			return err
		}
		return sqlDB.Close()
	}
	return nil
}

// getEnv adalah helper function untuk membaca environment variable dengan default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// InitializeDatabase adalah wrapper function untuk inisialisasi lengkap database
func InitializeDatabase() error {
	if err := ConnectDatabase(); err != nil {
		return err
	}
	
	if err := RunMigrations(); err != nil {
		return err
	}
	
	if err := CreateDefaultCategories(); err != nil {
		log.Printf("Warning: Failed to create default categories: %v", err)
		// Tidak return error karena ini tidak kritis
	}
	
	return nil
}