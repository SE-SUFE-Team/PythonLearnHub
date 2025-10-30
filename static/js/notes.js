// Notes frontend script: handles opening modal, listing, creating, updating, deleting notes
(function () {
    function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
    function qsa(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

    const notesModalEl = document.getElementById('notesModal');
    const notesModal = notesModalEl ? new bootstrap.Modal(notesModalEl) : null;
    const openNotesBtn = document.getElementById('openNotesBtn');
    const notesList = document.getElementById('notesList');
    const notesSearch = document.getElementById('notesSearch');
    const newNoteBtn = document.getElementById('newNoteBtn');
    const saveNoteBtn = document.getElementById('saveNoteBtn');
    const deleteNoteBtn = document.getElementById('deleteNoteBtn');
    const noteTitleInput = document.getElementById('noteTitle');
    const noteMeta = document.getElementById('noteMeta');

    let currentNoteId = null;
    let loading = false;

    function setLoading(v) { loading = !!v; if (saveNoteBtn) saveNoteBtn.disabled = loading; }

    async function fetchNotes(q) {
        const url = '/api/notes' + (q ? '?q=' + encodeURIComponent(q) : '');
        const res = await fetch(url);
        if (!res.ok) throw new Error('获取笔记失败');
        return res.json();
    }

    function renderNotes(list) {
        if (!notesList) return;
        notesList.innerHTML = '';
        if (!list || !list.length) {
            notesList.innerHTML = '<div class="text-muted p-3">暂无笔记</div>';
            return;
        }
        list.forEach(n => {
            const div = document.createElement('div');
            div.className = 'note-item d-flex justify-content-between align-items-start';
            div.dataset.noteId = n.note_id;
            const left = document.createElement('div');
            left.style.flex = '1';
            const title = document.createElement('div');
            title.className = 'fw-semibold';
            title.textContent = n.title || (n.content || '').slice(0, 60).replace(/\n/g, ' ');
            const meta = document.createElement('div');
            meta.className = 'note-meta small mt-1';
            meta.textContent = new Date(n.updated_at || n.created_at).toLocaleString();
            left.appendChild(title);
            left.appendChild(meta);

            const right = document.createElement('div');
            right.className = 'ms-2 text-end';
            const openBtn = document.createElement('button');
            openBtn.className = 'btn btn-sm btn-outline-primary me-1';
            openBtn.textContent = '打开';
            openBtn.addEventListener('click', (e) => { e.stopPropagation(); openNote(n.note_id); });

            const delBtn = document.createElement('button');
            delBtn.className = 'btn btn-sm btn-outline-danger';
            delBtn.innerHTML = '<i class="fas fa-trash"></i>';
            delBtn.title = '删除笔记';
            delBtn.addEventListener('click', (e) => { e.stopPropagation(); deleteNote(n.note_id); });

            right.appendChild(openBtn);
            right.appendChild(delBtn);

            div.appendChild(left);
            div.appendChild(right);

            div.addEventListener('click', () => { loadNoteIntoEditor(n); });

            notesList.appendChild(div);
        });
    }

    function loadNoteIntoEditor(n) {
        currentNoteId = n.note_id;
        noteTitleInput.value = n.title || '';
        setNoteContentValue(n.content || '');
        noteMeta.textContent = `最后更新: ${new Date(n.updated_at || n.created_at).toLocaleString()}`;
        
        deleteNoteBtn.classList.remove('d-none');
    }

    function clearEditor() {
        currentNoteId = null;
        noteTitleInput.value = '';
        setNoteContentValue('');
        noteMeta.textContent = '';
        deleteNoteBtn.classList.add('d-none');
    }

    async function openNote(id) {
        try {
            setLoading(true);
            const res = await fetch('/api/notes');
            const list = await res.json();
            const note = list.find(x => x.note_id === id);
            if (note) loadNoteIntoEditor(note);
        } catch (e) {
            console.error(e);
            alert('打开笔记失败');
        } finally { setLoading(false); }
    }

    

    async function saveNote() {
        const content = getNoteContentValue().trim();
        const title = noteTitleInput.value.trim();
        if (!content) { alert('笔记内容不能为空'); return; }
        try {
            setLoading(true);
            if (currentNoteId) {
                const res = await fetch('/api/notes/' + currentNoteId, {
                    method: 'PUT', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content })
                });
                if (!res.ok) throw new Error('更新失败');
            } else {
                const res = await fetch('/api/notes', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, content })
                });
                if (!res.ok) throw new Error('创建失败');
            }
            await refreshNotes();
            alert('保存成功');
        } catch (e) {
            console.error(e);
            alert('保存笔记失败');
        } finally { setLoading(false); }
    }

    async function deleteNote(id) {
        if (!confirm('确认删除该笔记？')) return;
        try {
            setLoading(true);
            const res = await fetch('/api/notes/' + id, { method: 'DELETE' });
            if (!res.ok) throw new Error('删除失败');
            if (currentNoteId === id) clearEditor();
            await refreshNotes();
        } catch (e) {
            console.error(e);
            alert('删除失败');
        } finally { setLoading(false); }
    }

    async function refreshNotes() {
        try {
            const q = notesSearch.value.trim();
            const list = await fetchNotes(q);
            renderNotes(list);
        } catch (e) {
            console.error(e);
            notesList.innerHTML = '<div class="text-muted p-3">加载失败</div>';
        }
    }

    

    // bind events
    if (openNotesBtn) openNotesBtn.addEventListener('click', async () => { clearEditor(); await refreshNotes(); notesModal.show(); });
    function focusNoteContent() {
        try {
            if (noteEditor && noteEditor.codemirror) {
                noteEditor.codemirror.focus();
            } else if (noteContentTextarea) {
                noteContentTextarea.focus();
            }
        } catch (e) { }
    }
    if (newNoteBtn) newNoteBtn.addEventListener('click', () => { clearEditor(); focusNoteContent(); });
    if (saveNoteBtn) saveNoteBtn.addEventListener('click', saveNote);
    if (deleteNoteBtn) deleteNoteBtn.addEventListener('click', () => { if (currentNoteId) deleteNote(currentNoteId); });
    if (notesSearch) notesSearch.addEventListener('input', debounce(async () => { await refreshNotes(); }, 300));

    // simple debounce
    function debounce(fn, t) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), t);
        };
    }

    // --------------------
    // Notes: 语音识别功能
    // --------------------
    let notesRecognition = null;
    let notesIsListening = false;
    // Markdown editor instance (EasyMDE)
    let noteEditor = null;
    const noteContentTextarea = document.getElementById('noteContent');

    function initNotesSpeechRecognition() {
        // 如果已经创建则复用
        if (notesRecognition) return;

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            // 浏览器不支持
            notesRecognition = null;
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        notesRecognition = new SpeechRecognition();
        notesRecognition.continuous = false;
        notesRecognition.interimResults = true;
        notesRecognition.lang = 'zh-CN';
        notesRecognition.maxAlternatives = 1;

        notesRecognition.onstart = function () {
            notesIsListening = true;
            updateNotesVoiceButtonState(true);
            showNotesVoiceStatus('正在监听...');
            console.log('Notes 语音识别开始');
        };

        notesRecognition.onresult = function (event) {
            let finalTranscript = '';
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (finalTranscript) {
                // 将最终识别结果追加到当前笔记内容
                const cur = getNoteContentValue() || '';
                setNoteContentValue(cur + (cur && !cur.endsWith('\n') ? '\n' : '') + finalTranscript.trim());
                focusNoteContent();
                showNotesVoiceStatus('识别完成');
            } else if (interimTranscript) {
                showNotesVoiceStatus(`识别中: ${interimTranscript}`);
            }
        };

        notesRecognition.onend = function () {
            notesIsListening = false;
            updateNotesVoiceButtonState(false);
            // 3s 后清除状态
            setTimeout(() => { showNotesVoiceStatus(''); }, 3000);
            console.log('Notes 语音识别结束');
        };

        notesRecognition.onerror = function (event) {
            notesIsListening = false;
            updateNotesVoiceButtonState(false);
            let msg = '语音识别出错';
            switch (event.error) {
                case 'no-speech': msg = '未检测到语音，请重试'; break;
                case 'audio-capture': msg = '无法访问麦克风，请检查权限'; break;
                case 'not-allowed': msg = '麦克风权限被拒绝'; break;
                case 'network': msg = '网络错误，请检查网络'; break;
            }
            showNotesVoiceStatus(msg, 'error');
            console.error('Notes 语音识别错误:', event);
        };
    }

    function toggleNotesVoice() {
        if (!notesRecognition) {
            initNotesSpeechRecognition();
            if (!notesRecognition) {
                alert('当前浏览器不支持语音识别功能');
                return;
            }
        }

        if (notesIsListening) {
            try { notesRecognition.stop(); } catch (e) { console.warn(e); }
        } else {
            try { notesRecognition.start(); } catch (e) {
                console.error('启动语音识别失败', e);
                showNotesVoiceStatus('启动失败', 'error');
            }
        }
    }

    function updateNotesVoiceButtonState(isListening) {
        const btn = document.getElementById('notesVoiceBtn');
        if (!btn) return;
        const icon = btn.querySelector('i');
        if (isListening) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-danger');
            if (icon) icon.className = 'fas fa-microphone-slash';
            btn.title = '停止语音输入';
        } else {
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-outline-secondary');
            if (icon) icon.className = 'fas fa-microphone';
            btn.title = '语音输入';
        }
    }

    function showNotesVoiceStatus(message, type = 'info') {
        const st = document.getElementById('notesVoiceStatus');
        if (!st) return;
        st.textContent = message || '';
        if (type === 'error') st.classList.add('text-danger'); else st.classList.remove('text-danger');
    }

    // 绑定语音按钮
    const notesVoiceBtn = document.getElementById('notesVoiceBtn');
    if (notesVoiceBtn) {
        notesVoiceBtn.addEventListener('click', function (e) {
            e.preventDefault();
            toggleNotesVoice();
        });
    }

    // 在模态显示时初始化识别器，隐藏时停止识别
    if (notesModalEl) {
        notesModalEl.addEventListener('shown.bs.modal', function () {
            initNotesSpeechRecognition();
            // 初始化或恢复 EasyMDE 编辑器
            try {
                if (typeof EasyMDE !== 'undefined' && !noteEditor && noteContentTextarea) {
                    noteEditor = new EasyMDE({
                        element: noteContentTextarea,
                        spellChecker: false,
                        autosave: { enabled: false },
                        status: false,
                        placeholder: '在此填写学习笔记，支持 Markdown 格式',
                        toolbar: ["bold", "italic", "heading", "|", "quote", "code", "unordered-list", "ordered-list", "link", "image", "|", "preview", "side-by-side", "fullscreen"]
                    });
                }
            } catch (e) {
                console.warn('初始化 Markdown 编辑器失败', e);
            }
        });
        notesModalEl.addEventListener('hidden.bs.modal', function () {
            if (notesRecognition && notesIsListening) {
                try { notesRecognition.stop(); } catch (e) { }
            }
            showNotesVoiceStatus('');
            // 不销毁 editor，这样编辑内容能保留。若想销毁，可调用 noteEditor.toTextArea() 并置为 null
        });
    }

    // helper to get/set content with editor fallback
    function getNoteContentValue() {
        if (noteEditor) return noteEditor.value();
        if (noteContentTextarea) return noteContentTextarea.value;
        return '';
    }

    function setNoteContentValue(val) {
        if (noteEditor) {
            noteEditor.value(val || '');
        } else if (noteContentTextarea) {
            noteContentTextarea.value = val || '';
        }
    }

    // initial no-op if modal not present
})();
