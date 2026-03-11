import React from 'react';

export const Card = ({ children, className = '', title, action }) => {
  return (
    <div className={`card ${className}`}>
      {(title || action) && (
        <div className="flex justify-between items-center mb-4">
          {title && <h3 className="text-lg text-gray-700">{title}</h3>}
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
