import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import ChatbotWidget from '@site/src/components/ChatbotWidget/ChatbotWidget';

// This component extends the default layout with the chatbot
export default function LayoutWrapper(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <ChatbotWidget />
    </>
  );
}