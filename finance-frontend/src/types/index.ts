export interface User {
  id: number;
  username: string;
}

export interface Category {
  id: number;
  name: string;
  user_id: number;
}

export interface Transaction {
  id: number;
  description: string;
  amount: number;
  transaction_date: string;
  category_id?: number;
  category_name?: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  ai_confidence?: number;
  prediction_method?: string;
}

export interface AuthResponse {
  token: string;
  user_id: number;
  username: string;
  message: string;
}

export interface TransactionSummary {
  total_income: number;
  total_expense: number;
  balance: number;
  transaction_count: number;
}
