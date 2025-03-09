import React from 'react';
import { Image } from '../types';

export function ImageCard({
  image,
  onDelete,
  onEdit,
  onAddAnnotation,
  onUpdateAnnotation,
}: {
  image: Image;
  onDelete: (key: string) => void;
  onEdit: (key: string) => void;
  onAddAnnotation: (key: string) => void;
  onUpdateAnnotation: (key: string, idx: number) => void;
}) {
  return (
    <div className="bg-white shadow rounded p-4">
      <img src={`http://localhost:8000${image.image_key}`} alt="" className="rounded" />
      <div className="mt-2 text-sm space-y-1">
      <p 
          className="text-sm overflow-hidden whitespace-nowrap text-ellipsis" 
          title={image.image_key}
        >
          <span className="font-semibold">Image Key:</span> {image.image_key}
        </p>
        <p><strong>Client:</strong> {image.client_id}</p>
        <p><strong>Location:</strong> {image.location_id}</p>
        <p><strong>User:</strong> {image.user_id}</p>
        <p><strong>ML Tag:</strong> {image.ml_tag}</p>

        {image.annotations.length > 0 && (
          <div className="mt-3">
            <strong>Annotations:</strong>
            {image.annotations.map(ann => (
              <div key={ann.index} className="flex items-center justify-between border-b py-1">
                <p>
                  <strong>{ann.index}.</strong> {ann.instrument} | Polygon: {JSON.stringify(ann.polygon)}
                </p>
                <button
                  className="bg-blue-500 text-white px-2 py-0.5 rounded text-xs"
                  onClick={() => onUpdateAnnotation(image.image_key, ann.index)}
                >
                  Edit
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-between mt-4">
        <button onClick={() => onEdit(image.image_key)} className="bg-green-500 text-white px-3 py-1 rounded">Edit Size</button>
        <button onClick={() => onAddAnnotation(image.image_key)} className="bg-yellow-500 text-white px-3 py-1 rounded">Add Annotation</button>
        <button onClick={() => onDelete(image.image_key)} className="bg-red-500 text-white px-3 py-1 rounded">Delete</button>
      </div>
    </div>
  );
}
