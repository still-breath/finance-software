package main

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

// JWT Claims structure
type Claims struct {
	UserID   uint   `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

// Request/Response structures
type RegisterRequest struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Password string `json:"password" binding:"required,min=6"`
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type AuthResponse struct {
	Token    string `json:"token"`
	UserID   uint   `json:"user_id"`
	Username string `json:"username"`
	Message  string `json:"message"`
}

type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message"`
}

var jwtSecret = []byte(getEnv("JWT_SECRET", "your-secret-key"))

// RegisterUser handles user registration
func RegisterUser(c *gin.Context) {
	var req RegisterRequest

	// Bind JSON request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	// Check if username already exists
	var existingUser User
	if err := DB.Where("username = ?", req.Username).First(&existingUser).Error; err == nil {
		c.JSON(http.StatusConflict, ErrorResponse{
			Error:   "username_exists",
			Message: "Username sudah digunakan",
		})
		return
	}

	// Hash password using bcrypt
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "hash_error",
			Message: "Gagal melakukan hash password",
		})
		return
	}

	// Create new user
	user := User{
		Username: req.Username,
		Password: string(hashedPassword),
	}

	if err := DB.Create(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Gagal menyimpan user ke database",
		})
		return
	}

	// Generate JWT token
	token, err := generateJWT(user.ID, user.Username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "token_error",
			Message: "Gagal membuat token",
		})
		return
	}

	c.JSON(http.StatusCreated, AuthResponse{
		Token:    token,
		UserID:   user.ID,
		Username: user.Username,
		Message:  "User berhasil didaftarkan",
	})
}

// LoginUser handles user authentication
func LoginUser(c *gin.Context) {
	var req LoginRequest

	// Bind JSON request
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "validation_error",
			Message: err.Error(),
		})
		return
	}

	// Find user by username
	var user User
	if err := DB.Where("username = ?", req.Username).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "invalid_credentials",
			Message: "Username atau password salah",
		})
		return
	}

	// Verify password
	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "invalid_credentials",
			Message: "Username atau password salah",
		})
		return
	}

	// Generate JWT token
	token, err := generateJWT(user.ID, user.Username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "token_error",
			Message: "Gagal membuat token",
		})
		return
	}

	c.JSON(http.StatusOK, AuthResponse{
		Token:    token,
		UserID:   user.ID,
		Username: user.Username,
		Message:  "Login berhasil",
	})
}

// generateJWT creates a new JWT token
func generateJWT(userID uint, username string) (string, error) {
	// Set token expiration (24 hours)
	expirationTime := time.Now().Add(24 * time.Hour)

	// Create claims
	claims := &Claims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expirationTime),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "finance-backend-go",
		},
	}

	// Create token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// Sign token
	tokenString, err := token.SignedString(jwtSecret)
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

// validateJWT validates JWT token and returns claims
func validateJWT(tokenString string) (*Claims, error) {
	claims := &Claims{}

	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtSecret, nil
	})

	if err != nil {
		return nil, err
	}

	if !token.Valid {
		return nil, jwt.ErrTokenInvalidClaims
	}

	return claims, nil
}
