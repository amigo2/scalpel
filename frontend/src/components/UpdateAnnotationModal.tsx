// components/UpdateAnnotationModal.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface UpdateAnnotationModalProps {
  isOpen: boolean;
  imageKey: string;
  annotationIndex: number;
  initialInstrument: string;
  initialPolygon: Record<string, unknown>;
  onClose: () => void;
  onUpdated?: () => void;
}

const UpdateAnnotationModal: React.FC<UpdateAnnotationModalProps> = ({
  isOpen,
  imageKey,
  annotationIndex,
  initialInstrument,
  initialPolygon,
  onClose,
  onUpdated,
}) => {
  const [instrument, setInstrument] = useState(initialInstrument);
  const [polygon, setPolygon] = useState(JSON.stringify(initialPolygon, null, 2));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setInstrument(initialInstrument);
    setPolygon(JSON.stringify(initialPolygon, null, 2));
  }, [initialInstrument, initialPolygon]);

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
      await axios.put(
        `http://localhost:8000/images/${encodeURIComponent(imageKey)}/annotations/${annotationIndex}`,
        { instrument, polygon: polygonJson }
      );
      onUpdated?.();
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
        <h2 className="text-xl font-semibold mb-4">Update Annotation</h2>
        {error && <div className="text-red-500 mb-2">{error}</div>}
        <form onSubmit={handleSubmit}>
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
              rows={4}
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
              className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded"
            >
              {loading ? "Updating..." : "Update"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UpdateAnnotationModal;
