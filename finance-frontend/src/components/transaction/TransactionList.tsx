import React from 'react';
import type { Transaction } from '../../types';
import { TransactionItem } from './TransactionItem';

interface TransactionListProps {
  // Tipe data diubah untuk mengizinkan null atau undefined dari API
  transactions: Transaction[] | null | undefined;
}

export const TransactionList: React.FC<TransactionListProps> = ({ transactions }) => {
  // PERBAIKAN: Tambahkan pengecekan untuk null atau undefined sebelum mengakses .length
  if (!transactions || transactions.length === 0) {
    return (
      <div className="text-center py-10 px-6 bg-white rounded-lg shadow-md">
        <h3 className="text-lg font-medium text-gray-900">Belum Ada Transaksi</h3>
        <p className="mt-1 text-sm text-gray-500">
          Silakan tambahkan transaksi baru untuk memulai.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <ul className="divide-y divide-gray-200">
        {transactions.map((tx) => (
          <TransactionItem key={tx.id} transaction={tx} />
        ))}
      </ul>
    </div>
  );
};

