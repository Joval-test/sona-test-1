import { useState } from 'react';

export const useNotification = () => {
  const [notification, setNotification] = useState({ type: '', message: '' });

  const showSuccess = (message = 'Operation successful') => {
    setNotification({ type: 'success', message });
  };

  const showError = (message = 'Operation failed') => {
    setNotification({ type: 'error', message });
  };

  const clearNotification = () => {
    setNotification({ type: '', message: '' });
  };

  return {
    notification,
    showSuccess,
    showError,
    clearNotification
  };
};

export default useNotification;
