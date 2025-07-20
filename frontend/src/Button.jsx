import React, { useState } from 'react';

function Button({ className = '', onClick, type = 'button', children, ...props }) {
  const [pressed, setPressed] = useState(false);

  return (
    <button
      type={type}
      className={className + (pressed ? ' pressed' : '')}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onMouseLeave={() => setPressed(false)}
      onTouchStart={() => setPressed(true)}
      onTouchEnd={() => setPressed(false)}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button; 