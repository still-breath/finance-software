import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import api from '../api/axios';
import type { AuthResponse, User } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const auth = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Password tidak cocok.');
      return;
    }
    if (password.length < 6) {
        setError('Password minimal 6 karakter.');
        return;
    }
    
    setIsLoading(true);
    setError('');

    try {
      const response = await api.post<AuthResponse>('/auth/register', { username, password });
      const { token, user_id, username: newUsername } = response.data;
      const user: User = { id: user_id, username: newUsername };
      auth.login(token, user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registrasi gagal. Coba username lain.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-800">Daftar Akun Baru</h2>
        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <div className="space-y-1">
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
            <Input id="username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div>
            <label htmlFor="password"  className="block text-sm font-medium text-gray-700">Password</label>
            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <div>
            <label htmlFor="confirmPassword"  className="block text-sm font-medium text-gray-700">Konfirmasi Password</label>
            <Input id="confirmPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          </div>
          <div>
            <Button type="submit" isLoading={isLoading}>
              Daftar
            </Button>
          </div>
        </form>
        <p className="text-sm text-center text-gray-600">
          Sudah punya akun?{' '}
          <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
            Login di sini
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
