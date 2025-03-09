import React from 'react';

export function TopBar({ title }: { title: string }) {
  return (
    <div className="bg-gray-800 text-white p-4">
      <h1 className="text-2xl font-bold text-center">{title}</h1>
    </div>
  );
}
