import React, { useState } from 'react';
import axios from 'axios';

interface NewAnnotationModalProps {
  isOpen: boolean;
  imageKey: string;
  onClose: () => void;
}

const NewAnnotationModal: React.FC<NewAnnotationModalProps> = ({ isOpen, imageKey, onClose }) => {
  const [index, setIndex] = useState(0);
  const [instrument, setInstrument] = useState("");
  const [polygon, setPolygon] = useState('{"points": [[0, 0], [1, 1]]}');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    let polygonJson;
    try {
      polygonJson = JSON.parse(polygon);
    } catch {
      setError("Invalid polygon JSON");
      setLoading(false);
      return;
    }

    try {
        await axios.post(
            `http://localhost:8000/images/${encodeURIComponent(imageKey)}/annotations`,
            { index, instrument, polygon: polygonJson }
          );
          
          
          
        onClose();
        } catch (err: any) {
        setError(err.response?.data?.detail || "An error occurred");
        } finally {
        setLoading(false);
        }
    };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded shadow max-w-md w-full">
        <h2 className="text-xl font-semibold mb-4">New Annotation</h2>
        {error && <div className="text-red-500 mb-2">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-2">
            <label className="block">Index</label>
            <input 
              type="number" 
              value={index} 
              onChange={(e) => setIndex(parseInt(e.target.value))}
              className="border rounded px-2 py-1 w-full"
            />
          </div>
          <div className="mb-2">
            <label className="block">Instrument</label>
            <input 
              type="text"
              value={instrument}
              onChange={(e) => setInstrument(e.target.value)}
              className="border rounded px-2 py-1 w-full"
            />
          </div>
          <div className="mb-2">
            <label className="block">Polygon (JSON)</label>
            <textarea
              value={polygon}
              onChange={(e) => setPolygon(e.target.value)}
              className="border rounded px-2 py-1 w-full"
              rows={3}
            />
          </div>
          <div className="mt-4 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
            >
              {loading ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewAnnotationModal;
