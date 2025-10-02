import React from 'react';
import type { Transaction } from '../../types';

interface TransactionItemProps {
  transaction: Transaction;
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
};

export const TransactionItem: React.FC<TransactionItemProps> = ({ transaction }) => {
  const isExpense = transaction.amount < 0;
  const amountColor = isExpense ? 'text-red-600' : 'text-green-600';
  
  return (
    <li className="flex items-center justify-between p-4 hover:bg-gray-50">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{transaction.description}</p>
        <p className="text-xs text-gray-500">{formatDate(transaction.transaction_date)}</p>
      </div>
      <div className="text-right ml-4">
        <p className={`text-sm font-semibold ${amountColor}`}>
          {formatCurrency(transaction.amount)}
        </p>
        <p className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full mt-1 inline-block">
          {transaction.category_name || 'Tanpa Kategori'}
        </p>
      </div>
    </li>
  );
};
