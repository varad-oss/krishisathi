import React, { useState } from 'react';
import { postExchangeSignal } from '@/lib/api';
import { useLanguage } from '@/lib/LanguageContext';
import { IndianState } from '@/lib/types';
import { t } from '@/lib/translations';

export default function SignalPublisher({ states, onPublish }: { states: IndianState[], onPublish: () => void }) {
  const { language } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [fromState, setFromState] = useState(states[0]?.code || 'MH');
  const [toState, setToState] = useState('');
  const [signalType, setSignalType] = useState('disease_alert');
  const [severity, setSeverity] = useState('moderate');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await postExchangeSignal({
        from_state: fromState,
        to_state: toState || null,
        signal_type: signalType,
        severity: severity,
        message: message,
      });
      setMessage('');
      setIsOpen(false);
      onPublish(); // Trigger refresh
    } catch (err) {
      alert("Failed to publish signal. Ensure backend is running and authenticated.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="w-full mt-4 py-2 border-2 border-dashed border-blue-200 text-blue-600 font-medium rounded-xl hover:bg-blue-50 transition-colors"
      >
        + {t("Publish Authenticated Signal (Nodal Officer)", language)}
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 p-4 border border-blue-100 bg-white rounded-xl shadow-sm space-y-3">
      <div className="flex justify-between items-center mb-2">
        <h4 className="font-bold text-gray-800 text-sm">🔒 {t("Authenticated Federation Network", language)}</h4>
        <button type="button" onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600">✕</button>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">{t("From State", language)}</label>
          <select value={fromState} onChange={e => setFromState(e.target.value)} className="w-full border rounded p-1.5 text-sm">
            {states.map(s => <option key={s.code} value={s.code}>{s.name} ({s.code})</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">{t("To State (Optional)", language)}</label>
          <select value={toState} onChange={e => setToState(e.target.value)} className="w-full border rounded p-1.5 text-sm">
            <option value="">{t("All States (Broadcast)", language)}</option>
            {states.map(s => <option key={s.code} value={s.code}>{s.name} ({s.code})</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">{t("Signal Type", language)}</label>
          <select value={signalType} onChange={e => setSignalType(e.target.value)} className="w-full border rounded p-1.5 text-sm">
            <option value="disease_alert">Disease Alert</option>
            <option value="pest_advisory">Pest Advisory</option>
            <option value="weather_advisory">Weather Advisory</option>
            <option value="best_practice">Best Practice</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">{t("Severity", language)}</label>
          <select value={severity} onChange={e => setSeverity(e.target.value)} className="w-full border rounded p-1.5 text-sm">
            <option value="info">Info</option>
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-700 mb-1">{t("Message", language)}</label>
        <textarea 
          required 
          value={message} 
          onChange={e => setMessage(e.target.value)} 
          className="w-full border rounded p-2 text-sm" 
          rows={2} 
          placeholder={t("Enter aggregated, anonymized intelligence...", language)}
        />
      </div>
      
      <button 
        type="submit" 
        disabled={loading}
        className="w-full bg-blue-600 text-white font-medium py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
      >
        {loading ? t("Authenticating & Publishing...", language) : t("Publish Secure Signal", language)}
      </button>
    </form>
  );
}
