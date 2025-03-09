import React from 'react';
import { Image } from '../types';
import { ImageCard } from './ImageCard';

export function ImagesGrid({
  images,
  onDelete,
  onEdit,
  onAddAnnotation,
  onUpdateAnnotation,
}: {
  images: Image[];
  onDelete: (key: string) => void;
  onEdit: (key: string) => void;
  onAddAnnotation: (key: string) => void;
  onUpdateAnnotation: (key: string, idx: number) => void;
}) {
  return (
    <div className="grid grid-cols-3 gap-6">
      {images.map(img => (
        <ImageCard
          key={img.image_key}
          image={img}
          onDelete={onDelete}
          onEdit={onEdit}
          onAddAnnotation={onAddAnnotation}
          onUpdateAnnotation={onUpdateAnnotation}
        />
      ))}
    </div>
  );
}
