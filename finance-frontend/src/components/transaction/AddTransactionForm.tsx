import React, { useState, type FormEvent } from 'react';
import api from '../../api/axios';
import type { Transaction } from '../../types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface AddTransactionFormProps {
  onTransactionAdded: (transaction: Transaction) => void;
}

export const AddTransactionForm: React.FC<AddTransactionFormProps> = ({ onTransactionAdded }) => {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastAdded, setLastAdded] = useState<Transaction | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setLastAdded(null);

    try {
      const response = await api.post<{ transaction: Transaction }>('/transactions', {
        description,
        amount: parseFloat(amount),
      });
      onTransactionAdded(response.data.transaction);
      setLastAdded(response.data.transaction);
      setDescription('');
      setAmount('');
    } catch (err) {
      setError('Gagal menambahkan transaksi.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Tambah Transaksi Baru</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Deskripsi (cth: Beli Kopi, Bayar Listrik)
          </label>
          <Input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            placeholder="Makan siang di warteg"
          />
        </div>
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700">
            Jumlah (Gunakan - untuk pengeluaran)
          </label>
          <Input
            id="amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
            placeholder="-25000"
          />
        </div>
        <Button type="submit" isLoading={isLoading} className="w-auto px-6">
          Tambah
        </Button>
      </form>
      {lastAdded && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md text-sm text-green-700">
          Berhasil ditambahkan! Kategori oleh AI: <span className="font-bold">{lastAdded.category_name}</span>
        </div>
      )}
    </div>
  );
};
