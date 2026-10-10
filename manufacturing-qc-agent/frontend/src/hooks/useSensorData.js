/**
 * useSensorData hook — polls latest sensor readings and dashboard summary.
 */
import { useState, useEffect, useCallback } from 'react';
import { getDashboardSummary, getLatestReadings, getAlerts } from '../api/client';

export function useSensorData(intervalMs = 3000) {
  const [summary,  setSummary]  = useState(null);
  const [readings, setReadings] = useState({});
  const [alerts,   setAlerts]   = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [summaryRes, readingsRes, alertsRes] = await Promise.allSettled([
        getDashboardSummary(),
        getLatestReadings(),
        getAlerts(),
      ]);
      if (summaryRes.status  === 'fulfilled') setSummary(summaryRes.value.data);
      if (readingsRes.status === 'fulfilled') setReadings(readingsRes.value.data.readings || {});
      if (alertsRes.status   === 'fulfilled') setAlerts(alertsRes.value.data.alerts || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, intervalMs);
    return () => clearInterval(id);
  }, [fetchAll, intervalMs]);

  return { summary, readings, alerts, loading, error, refetch: fetchAll };
}
