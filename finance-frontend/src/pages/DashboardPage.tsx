import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';
import type { Transaction, TransactionSummary } from '../types';
import { AddTransactionForm } from '../components/transaction/AddTransactionForm';
import { TransactionList } from '../components/transaction/TransactionList';
import { Spinner } from '../components/ui/Spinner';

const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(amount);
};

const DashboardPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // useCallback dibuat stabil dengan dependency array kosong []
  const fetchData = useCallback(async () => {
    setError('');
    try {
      // Ambil data transaksi dan ringkasan secara bersamaan
      const [transResponse, summaryResponse] = await Promise.all([
        api.get<{ transactions: Transaction[] }>('/transactions'),
        api.get<{ summary: TransactionSummary }>('/stats/summary'),
      ]);
      setTransactions(transResponse.data.transactions);
      setSummary(summaryResponse.data.summary);
    } catch (err) {
      setError('Gagal memuat data. Silakan coba refresh halaman.');
    } finally {
      // Pastikan loading selalu dihentikan setelah selesai
      setIsLoading(false);
    }
  }, []); // <-- Array kosong ini penting agar fungsi tidak dibuat ulang

  // useEffect sekarang aman menggunakan fetchData sebagai dependency
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleTransactionAdded = () => {
    // Cukup panggil fetchData untuk mengambil data terbaru dari server
    fetchData(); 
  };
  
  if (isLoading) {
    return <div className="flex justify-center mt-10"><Spinner /></div>;
  }

  if (error) {
    return <p className="text-center text-red-500 mt-10">{error}</p>;
  }

  return (
    <div className="space-y-8">
      {/* Bagian Ringkasan */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Ringkasan Keuangan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-sm font-medium text-gray-500">Total Pemasukan</h3>
                <p className="mt-1 text-2xl font-semibold text-green-600">{formatCurrency(summary?.total_income || 0)}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-sm font-medium text-gray-500">Total Pengeluaran</h3>
                <p className="mt-1 text-2xl font-semibold text-red-600">{formatCurrency(summary?.total_expense || 0)}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-sm font-medium text-gray-500">Saldo Akhir</h3>
                <p className="mt-1 text-2xl font-semibold text-blue-600">{formatCurrency(summary?.balance || 0)}</p>
            </div>
        </div>
      </div>
      
      {/* Bagian Transaksi */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <div className="lg:col-span-1">
           <AddTransactionForm onTransactionAdded={handleTransactionAdded} />
        </div>
        <div className="lg:col-span-2">
           <h2 className="text-2xl font-bold text-gray-800 mb-4">Transaksi Terakhir</h2>
           <TransactionList transactions={transactions} />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

