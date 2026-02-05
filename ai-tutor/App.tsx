import React, { useState } from 'react';
import { StyleSheet, View, ScrollView, KeyboardAvoidingView, Platform, SafeAreaView } from 'react-native';
import { Provider as PaperProvider, TextInput, Button, Text, Card, Avatar, ActivityIndicator } from 'react-native-paper';
import { chatWithAI } from './services/api';

type Message = {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  sources?: any[];
};

export default function App() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), text: question, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);

    try {
      const response = await chatWithAI(userMsg.text);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        sender: 'ai',
        sources: response.sources
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg: Message = { id: Date.now().toString(), text: "Error connecting to AI Tutor.", sender: 'ai' };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PaperProvider>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text variant="headlineMedium" style={styles.headerTitle}>AI Books Tutor</Text>
        </View>

        <ScrollView style={styles.chatContainer} contentContainerStyle={{ padding: 16 }}>
          {messages.length === 0 && (
            <View style={styles.welcome}>
              <Text variant="bodyLarge" style={{ textAlign: 'center', color: '#666' }}>
                Ask a question about your uploaded books!
              </Text>
            </View>
          )}

          {messages.map((msg) => (
            <View key={msg.id} style={[
              styles.bubble,
              msg.sender === 'user' ? styles.userBubble : styles.aiBubble
            ]}>
              <Text style={msg.sender === 'user' ? styles.userText : styles.aiText}>
                {msg.text}
              </Text>
              {msg.sources && msg.sources.length > 0 && (
                <Text variant="labelSmall" style={{ marginTop: 8, color: '#666' }}>
                  Source: {msg.sources[0]?.source}
                </Text>
              )}
            </View>
          ))}

          {loading && (
            <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 10 }}>
              <ActivityIndicator animating={true} color="#6200ee" size="small" />
              <Text style={{ marginLeft: 10, color: '#666' }}>Thinking...</Text>
            </View>
          )}
        </ScrollView>

        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"}>
          <View style={styles.inputContainer}>
            <TextInput
              mode="outlined"
              placeholder="Ask a question..."
              value={question}
              onChangeText={setQuestion}
              style={styles.input}
              right={<TextInput.Icon icon="send" onPress={handleSend} />}
              onSubmitEditing={handleSend}
            />
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    alignItems: 'center'
  },
  headerTitle: {
    fontWeight: 'bold',
    color: '#6200ee'
  },
  chatContainer: {
    flex: 1,
  },
  welcome: {
    marginTop: 100,
    alignItems: 'center',
  },
  bubble: {
    padding: 15,
    borderRadius: 15,
    marginBottom: 10,
    maxWidth: '85%',
  },
  userBubble: {
    backgroundColor: '#6200ee',
    alignSelf: 'flex-end',
    borderBottomRightRadius: 2,
  },
  aiBubble: {
    backgroundColor: 'white',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 2,
    borderWidth: 1,
    borderColor: '#eee'
  },
  userText: {
    color: 'white',
  },
  aiText: {
    color: '#333',
  },
  inputContainer: {
    padding: 10,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  input: {
    backgroundColor: 'white',
  },
});
