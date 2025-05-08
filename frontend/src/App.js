import React, { useEffect, useState, useRef } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import axios from "axios";
import "./App.css";

const docId = new URLSearchParams(window.location.search).get("docId");

if (!docId) {
  alert("Missing docId in URL");
  throw new Error("Missing docId");
}


function App() {
  const [ws, setWs] = useState(null);
  const editorRef = useRef(null);

  const editor = useEditor({
    extensions: [StarterKit],
    content: "<p>Loading...</p>",
    onUpdate({ editor }) {
      const html = editor.getHTML();
      if (ws && ws.readyState === 1) {
        ws.send(html);
      }
    
      axios.put(`http://localhost:8000/documents/${docId}`, {
        content: html
      }).catch(err => {
        console.error("PUT failed:", err);
      });
    }    
  });

  useEffect(() => {
    // Load doc content
    axios.get(`http://localhost:8000/documents/${docId}`).then(res => {
      editor?.commands.setContent(res.data.content || "<p>New doc</p>");
    });

    // Setup WebSocket
    const socket = new WebSocket(`ws://localhost:8000/ws/${docId}`);
    socket.onmessage = (event) => {
      if (!editor?.isFocused) {
        editor?.commands.setContent(event.data);
      }
    };
    setWs(socket);
    editorRef.current = editor;

    return () => socket.close();
  }, [editor]);

  return (
    <div className="App">
      <h2>📝 Collaborative Editor</h2>
      <EditorContent editor={editor} />
    </div>
  );
}

export default App;
