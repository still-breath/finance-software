package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	// Load environment variables
	loadEnvironment()

	// Test AI service connection on startup
	log.Println("🔍 Testing AI service connection...")
	if err := TestAIService(); err != nil {
		log.Printf("⚠️ AI service test failed: %v", err)
		log.Println("📝 Application will continue with basic functionality")
	} else {
		log.Println("✅ AI service connection successful")
	}

	// Initialize database
	if err := InitializeDatabase(); err != nil {
		log.Fatal("Failed to initialize database:", err)
	}
	defer CloseDatabase()

	// Initialize Gin router
	router := setupRouter()

	// Setup routes
	setupRoutes(router)

	// Get port from environment
	port := getEnv("PORT", "8080")

	log.Printf("🚀 Server starting on port %s", port)
	log.Printf("📚 API Documentation available at: http://localhost:%s/health", port)
	log.Printf("🤖 AI Service URL: %s", getEnv("AI_SERVICE_URL", "http://localhost:5000"))

	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

func setupRouter() *gin.Engine {
	// Set Gin mode based on environment
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// CORS configuration
	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	config.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"Origin", "Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token", "Authorization", "accept", "origin", "Cache-Control", "X-Requested-With"}
	config.ExposeHeaders = []string{"Content-Length"}
	config.AllowCredentials = true

	router.Use(cors.New(config))

	// Recovery middleware
	router.Use(gin.Recovery())

	// Request logging middleware (optional)
	router.Use(gin.Logger())

	return router
}

func setupRoutes(router *gin.Engine) {
	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "finance-backend-go",
			"version": "1.0.0",
		})
	})

	// API v1 routes
	v1 := router.Group("/api/v1")
	{
		// Public routes (no authentication required)
		auth := v1.Group("/auth")
		{
			auth.POST("/register", RegisterUser)
			auth.POST("/login", LoginUser)
		}

		// Protected routes (JWT authentication required)
		protected := v1.Group("/")
		protected.Use(JWTMiddleware())
		{
			// User profile routes
			protected.GET("/profile", GetUserProfile)

			// Category routes
			protected.GET("/categories", GetCategories)
			protected.POST("/categories", CreateCategory)

			// Transaction routes
			protected.POST("/transactions", CreateTransaction)
			protected.GET("/transactions", GetTransactions)
			protected.GET("/transactions/:id", GetTransactionByID)
			protected.PUT("/transactions/:id", UpdateTransaction)
			protected.DELETE("/transactions/:id", DeleteTransaction)

			// AI Integration routes
			protected.PUT("/transactions/:id/recategorize", RecategorizeTransaction)
			protected.POST("/transactions/batch-recategorize", BatchRecategorize)
			protected.POST("/ai/test", TestAIServiceEndpoint)
			protected.GET("/ai/status", GetAIServiceStatus)

			// Enhanced category routes
			protected.GET("/categories/suggest", SuggestCategories)
			protected.GET("/categories/stats", GetCategoryStats)

			// Export routes
			protected.GET("/export/transactions", ExportTransactions)

			// Statistics routes
			protected.GET("/stats/summary", GetTransactionSummary)
			protected.GET("/stats/monthly", GetMonthlyStats)
		}
	}
}

// Additional handlers that might be needed
func GetUserProfile(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "unauthorized",
			Message: "User ID tidak ditemukan",
		})
		return
	}

	var user User
	if err := DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "user_not_found",
			Message: "User tidak ditemukan",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
		},
	})
}

func GetCategories(c *gin.Context) {
	userID, _ := c.Get("user_id")

	var categories []Category
	// Get user categories and system categories (user_id IS NULL)
	if err := DB.Where("user_id = ? OR user_id IS NULL", userID).Find(&categories).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengambil data kategori",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"categories": categories,
	})
}

func CreateCategory(c *gin.Context) {
	var req struct {
		Name string `json:"name" binding:"required,max=100"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	userID, _ := c.Get("user_id")

	category := Category{
		Name:   req.Name,
		UserID: userID.(uint),
	}

	if err := DB.Create(&category).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal membuat kategori",
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message":  "Kategori berhasil dibuat",
		"category": category,
	})
}

func GetTransactionByID(c *gin.Context) {
	userID, _ := c.Get("user_id")
	transactionID := c.Param("id")

	var transaction Transaction
	if err := DB.Preload("Category").Where("id = ? AND user_id = ?", transactionID, userID).First(&transaction).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "transaction_not_found",
			Message: "Transaksi tidak ditemukan",
		})
		return
	}

	var categoryName string
	if transaction.Category != nil {
		categoryName = transaction.Category.Name
	}

	response := TransactionResponse{
		ID:              transaction.ID,
		Description:     transaction.Description,
		Amount:          transaction.Amount,
		TransactionDate: transaction.TransactionDate,
		CategoryID:      transaction.CategoryID,
		CategoryName:    categoryName,
		UserID:          transaction.UserID,
		CreatedAt:       transaction.CreatedAt,
		UpdatedAt:       transaction.UpdatedAt,
	}

	c.JSON(http.StatusOK, gin.H{
		"transaction": response,
	})
}

func UpdateTransaction(c *gin.Context) {
	userID, _ := c.Get("user_id")
	transactionID := c.Param("id")

	var req CreateTransactionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	var transaction Transaction
	if err := DB.Where("id = ? AND user_id = ?", transactionID, userID).First(&transaction).Error; err != nil {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "transaction_not_found",
			Message: "Transaksi tidak ditemukan",
		})
		return
	}

	// Update fields
	transaction.Description = req.Description
	transaction.Amount = req.Amount
	if req.TransactionDate != nil {
		transaction.TransactionDate = *req.TransactionDate
	}

	if err := DB.Save(&transaction).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengupdate transaksi",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Transaksi berhasil diupdate",
	})
}

func DeleteTransaction(c *gin.Context) {
	userID, _ := c.Get("user_id")
	transactionID := c.Param("id")

	result := DB.Where("id = ? AND user_id = ?", transactionID, userID).Delete(&Transaction{})
	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal menghapus transaksi",
		})
		return
	}

	if result.RowsAffected == 0 {
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "transaction_not_found",
			Message: "Transaksi tidak ditemukan",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Transaksi berhasil dihapus",
	})
}

func GetTransactionSummary(c *gin.Context) {
	userID, _ := c.Get("user_id")

	var totalIncome, totalExpense float64
	var transactionCount int64

	// Count total transactions
	DB.Model(&Transaction{}).Where("user_id = ?", userID).Count(&transactionCount)

	// Sum positive amounts (income)
	DB.Model(&Transaction{}).Where("user_id = ? AND amount > 0", userID).Select("COALESCE(SUM(amount), 0)").Scan(&totalIncome)

	// Sum negative amounts (expenses)
	DB.Model(&Transaction{}).Where("user_id = ? AND amount < 0", userID).Select("COALESCE(SUM(ABS(amount)), 0)").Scan(&totalExpense)

	balance := totalIncome - totalExpense

	c.JSON(http.StatusOK, gin.H{
		"summary": gin.H{
			"total_income":      totalIncome,
			"total_expense":     totalExpense,
			"balance":           balance,
			"transaction_count": transactionCount,
		},
	})
}

func GetMonthlyStats(c *gin.Context) {
	userID, _ := c.Get("user_id")

	type MonthlyData struct {
		Month   string  `json:"month"`
		Income  float64 `json:"income"`
		Expense float64 `json:"expense"`
		Balance float64 `json:"balance"`
	}

	var monthlyStats []MonthlyData

	// Query untuk mendapatkan statistik bulanan (6 bulan terakhir)
	query := `
		SELECT 
			TO_CHAR(transaction_date, 'YYYY-MM') as month,
			COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as income,
			COALESCE(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 0) as expense
		FROM transactions 
		WHERE user_id = ? 
			AND transaction_date >= NOW() - INTERVAL '6 months'
		GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
		ORDER BY month DESC
	`

	rows, err := DB.Raw(query, userID).Rows()
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal mengambil statistik bulanan",
		})
		return
	}
	defer rows.Close()

	for rows.Next() {
		var data MonthlyData
		if err := rows.Scan(&data.Month, &data.Income, &data.Expense); err != nil {
			continue
		}
		data.Balance = data.Income - data.Expense
		monthlyStats = append(monthlyStats, data)
	}

	c.JSON(http.StatusOK, gin.H{
		"monthly_stats": monthlyStats,
	})
}

func loadEnvironment() {
	// Set default values if environment variables are not set
	if os.Getenv("JWT_SECRET") == "" {
		log.Println("Warning: JWT_SECRET not set, using default value")
	}
	if os.Getenv("DATABASE_DSN") == "" {
		log.Println("Warning: DATABASE_DSN not set, using default database configuration")
	}
}
