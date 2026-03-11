import React from 'react';

export const Badge = ({ type = 'success', children, icon: Icon }) => {
    const styles = {
        success: 'success',
        warning: 'warning',
        danger: 'danger',
        normal: 'bg-gray-100 text-gray-800'
    };

    return (
        <span className={`badge ${styles[type] || styles.normal}`}>
            {Icon && <Icon size={14} />}
            {children}
        </span>
    );
};
