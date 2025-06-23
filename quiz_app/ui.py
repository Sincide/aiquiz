import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import List, Dict, Set
import json

from .data import Question
from .db import save_result, is_favorite, mark_favorite, get_results_summary, get_favorite_questions
from .ollama import ask_model


class QuizUI:
    def __init__(self, root: tk.Tk, questions: List[Question], conn, model: str):
        self.root = root
        self.all_questions = questions
        self.questions = questions.copy()
        self.conn = conn
        self.model = model
        self.index = 0
        self.user_answer = None
        self.order_items = []
        self.selected_domains = set()
        self.quiz_mode = 'normal'  # 'normal', 'favorites', 'review'
        self.setup_styling()
        self.build_ui()
        self.show_domain_selection()

    def setup_styling(self):
        """Setup custom styling and themes"""
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Font fallback system
        try:
            # Try to use better fonts, fallback to system defaults
            import tkinter.font as tkfont
            families = tkfont.families()
            
            if 'Inter' in families:
                self.font_family = 'Inter'
            elif 'SF Pro Display' in families:
                self.font_family = 'SF Pro Display'
            elif 'Segoe UI' in families:
                self.font_family = 'Segoe UI'
            elif 'DejaVu Sans' in families:
                self.font_family = 'DejaVu Sans'
            else:
                self.font_family = 'Arial'
                
            if 'JetBrains Mono' in families:
                self.mono_font = 'JetBrains Mono'
            elif 'SF Mono' in families:
                self.mono_font = 'SF Mono'
            elif 'DejaVu Sans Mono' in families:
                self.mono_font = 'DejaVu Sans Mono'
            else:
                self.mono_font = 'Courier'
                
        except Exception:
            self.font_family = 'Arial'
            self.mono_font = 'Courier'
        
        # Custom colors
        self.colors = {
            'bg_primary': '#0f0f0f',
            'bg_secondary': '#1a1a1a', 
            'bg_tertiary': '#2d2d2d',
            'accent': '#3d5a80',
            'accent_hover': '#4a6b94',
            'success': '#2d7d32',
            'warning': '#f57c00',
            'error': '#d32f2f',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'text_muted': '#808080'
        }
        
        # Configure progressbar
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])

    def center_window(self, window, width=None, height=None):
        """Center a window on the active monitor (multi-monitor aware)"""
        if width and height:
            window.geometry(f'{width}x{height}')
        
        # Force update to ensure window dimensions are set
        window.update_idletasks()
        window.update()
        
        # Small delay to let Hyprland process the window
        window.after(10, lambda: self._do_center(window))
    
    def _do_center(self, window):
        """Actually perform the centering on the active monitor"""
        try:
            # Ensure window is updated
            window.update_idletasks()
            
            # Get window dimensions
            w_width = window.winfo_width()
            w_height = window.winfo_height()
            
            # For multi-monitor setups, we need to center on the active monitor
            # Get the main window position to determine which monitor we're on
            try:
                main_x = self.root.winfo_x()
                main_y = self.root.winfo_y()
                main_width = self.root.winfo_width()
                main_height = self.root.winfo_height()
                
                # Calculate center of main window
                main_center_x = main_x + main_width // 2
                main_center_y = main_y + main_height // 2
                
                # Position dialog centered on the main window's monitor
                x = main_center_x - w_width // 2
                y = main_center_y - w_height // 2
                
            except:
                # Fallback to simple screen centering if main window position fails
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                
                # Try to detect monitor boundaries (assume roughly equal monitors)
                # This is a heuristic for common multi-monitor setups
                monitor_width = 2560  # Based on your monitor config
                monitor_height = 1440
                
                # Center on primary monitor (usually leftmost or center)
                if screen_width > monitor_width * 2:  # Multi-monitor detected
                    x = monitor_width // 2 - w_width // 2
                    y = monitor_height // 2 - w_height // 2
                else:
                    x = (screen_width - w_width) // 2
                    y = (screen_height - w_height) // 2
            
            # Ensure window stays on screen
            x = max(0, x)
            y = max(0, y)
            
            # Apply position
            window.geometry(f'{w_width}x{w_height}+{x}+{y}')
            
            # Force window to front and focus
            window.lift()
            window.attributes('-topmost', True)
            window.after(10, lambda: window.attributes('-topmost', False))
            
        except Exception as e:
            print(f"Warning: Could not center window: {e}")
            # Fallback: just ensure window is visible
            window.geometry(f'+100+100')

    def build_ui(self):
        self.root.title('CISSP Quiz Application')
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.geometry('900x800')
        self.center_window(self.root, 900, 800)
        
        # Key bindings
        self.root.bind('<Left>', lambda e: self.prev_question())
        self.root.bind('<Right>', lambda e: self.next_question())
        self.root.bind('<Return>', lambda e: self.submit_or_next())
        self.root.bind('<Escape>', lambda e: self.root.quit())

        # Menu bar with better styling
        menubar = tk.Menu(self.root, 
                         bg=self.colors['bg_secondary'], 
                         fg=self.colors['text_primary'],
                         activebackground=self.colors['accent'],
                         activeforeground=self.colors['text_primary'])
        self.root.config(menu=menubar)
        
        quiz_menu = tk.Menu(menubar, tearoff=0, 
                           bg=self.colors['bg_secondary'], 
                           fg=self.colors['text_primary'])
        menubar.add_cascade(label="Quiz", menu=quiz_menu)
        quiz_menu.add_command(label="New Quiz", command=self.show_domain_selection)
        quiz_menu.add_command(label="Review Favorites", command=self.review_favorites)
        quiz_menu.add_command(label="Statistics", command=self.show_statistics)
        quiz_menu.add_separator()
        quiz_menu.add_command(label="Exit", command=self.root.quit)

        # Main content frame with padding
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_frame.pack(fill='both', expand=True, padx=40, pady=30)

        # Progress section
        progress_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        progress_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(progress_frame, 
                text="Progress", 
                bg=self.colors['bg_primary'],
                fg=self.colors['text_secondary'],
                font=(self.font_family, 10, 'bold')).pack(anchor='w')
         
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x', pady=(5, 0))

        # Info section
        self.lbl_info = tk.Label(
            self.main_frame, 
            text='', 
            fg=self.colors['text_secondary'], 
            bg=self.colors['bg_primary'],
            font=(self.font_family, 11)
        )
        self.lbl_info.pack(pady=(0, 20))

        # Question section with card-like appearance
        question_card = tk.Frame(self.main_frame, 
                                bg=self.colors['bg_secondary'],
                                relief='flat',
                                bd=1)
        question_card.pack(fill='x', pady=(0, 30))
        
        # Add subtle border effect
        border_frame = tk.Frame(question_card, 
                               bg=self.colors['bg_tertiary'], 
                               height=1)
        border_frame.pack(fill='x', side='top')
        
        self.txt_question = tk.Label(
            question_card, 
            text='', 
            wraplength=800, 
            fg=self.colors['text_primary'], 
            bg=self.colors['bg_secondary'],
            font=(self.font_family, 14),
            justify='left',
            pady=25,
            padx=25
        )
        self.txt_question.pack(fill='x')

        # Choices section
        self.frame_choices = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.frame_choices.pack(fill='both', expand=True, pady=(0, 30))

        # Button section with better layout
        self.frame_buttons = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.frame_buttons.pack(fill='x')

        # Left side buttons
        left_buttons = tk.Frame(self.frame_buttons, bg=self.colors['bg_primary'])
        left_buttons.pack(side='left')

        self.btn_prev = self.create_button(
            left_buttons, '← Previous', self.prev_question,
            bg=self.colors['bg_tertiary'], width=12
        )
        self.btn_prev.pack(side='left', padx=(0, 10))

        self.btn_fav = self.create_button(
            left_buttons, '★ Favorite', self.toggle_fav,
            bg=self.colors['warning'], width=12
        )
        self.btn_fav.pack(side='left', padx=(0, 10))

        self.btn_explain = self.create_button(
            left_buttons, '💡 Explain', self.explain,
            bg=self.colors['accent'], width=12
        )
        self.btn_explain.pack(side='left')

        # Right side buttons
        right_buttons = tk.Frame(self.frame_buttons, bg=self.colors['bg_primary'])
        right_buttons.pack(side='right')

        self.btn_next = self.create_button(
            right_buttons, 'Submit →', self.next_question,
            bg=self.colors['success'], width=12
        )
        self.btn_next.pack(side='right')

    def create_button(self, parent, text, command, bg=None, width=10):
        """Create a styled button"""
        if not bg:
            bg = self.colors['bg_tertiary']
            
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=self.colors['text_primary'],
            font=(self.font_family, 10, 'bold'),
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            width=width,
            cursor='hand2'
        )
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=self.lighten_color(bg))
        def on_leave(e):
            btn.config(bg=bg)
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn

    def lighten_color(self, color):
        """Lighten a hex color for hover effect"""
        if color == self.colors['bg_tertiary']:
            return '#404040'
        elif color == self.colors['accent']:
            return self.colors['accent_hover']
        elif color == self.colors['success']:
            return '#4caf50'
        elif color == self.colors['warning']:
            return '#ff9800'
        else:
            return color

    def create_dialog(self, title, width=500, height=400):
        """Create a properly positioned dialog window"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        self.center_window(dialog, width, height)
        
        # Prevent resize if dialog is small
        if width < 600:
            dialog.resizable(False, False)
            
        return dialog

    def show_domain_selection(self):
        """Show domain selection dialog with better styling"""
        domains = sorted(set(q.domain for q in self.all_questions))
        
        dialog = self.create_dialog("Select CISSP Domains", 600, 500)

        # Header
        header = tk.Label(
            dialog, 
            text="Choose domains for your quiz session", 
            fg=self.colors['text_primary'], 
            bg=self.colors['bg_primary'],
            font=(self.font_family, 16, 'bold')
        )
        header.pack(pady=(20, 30))

        # Scrollable domain list
        canvas = tk.Canvas(dialog, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Domain checkboxes with better styling
        self.domain_vars = {}
        for domain in domains:
            var = tk.BooleanVar(value=True)
            self.domain_vars[domain] = var
            
            frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], relief='flat')
            frame.pack(fill='x', padx=20, pady=5)
            
            cb = tk.Checkbutton(
                frame,
                text=f"{domain} ({sum(1 for q in self.all_questions if q.domain == domain)} questions)",
                variable=var,
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'],
                selectcolor=self.colors['accent'],
                font=(self.font_family, 11),
                pady=10,
                padx=15
            )
            cb.pack(anchor='w', fill='x')

        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=(0, 20))

        # Button section
        button_frame = tk.Frame(dialog, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.create_button(
            button_frame, "Select All",
            lambda: [var.set(True) for var in self.domain_vars.values()],
            bg=self.colors['bg_tertiary']
        ).pack(side='left', padx=(0, 10))

        self.create_button(
            button_frame, "Clear All", 
            lambda: [var.set(False) for var in self.domain_vars.values()],
            bg=self.colors['bg_tertiary']
        ).pack(side='left')

        self.create_button(
            button_frame, "Start Quiz",
            lambda: self.start_quiz(dialog),
            bg=self.colors['success']
        ).pack(side='right')

    def start_quiz(self, dialog):
        """Start quiz with selected domains"""
        selected = [domain for domain, var in self.domain_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Warning", "Please select at least one domain.")
            return
            
        dialog.destroy()
        self.selected_domains = set(selected)
        self.questions = [q for q in self.all_questions if q.domain in selected]
        random.shuffle(self.questions)
        self.index = 0
        self.quiz_mode = 'normal'
        self.show_question()

    def review_favorites(self):
        """Show favorite questions for review"""
        fav_ids = get_favorite_questions(self.conn)
        if not fav_ids:
            messagebox.showinfo("Info", "No favorite questions found.")
            return
            
        self.questions = [q for q in self.all_questions if q.id in fav_ids]
        random.shuffle(self.questions)
        self.index = 0
        self.quiz_mode = 'favorites'
        self.show_question()

    def show_statistics(self):
        """Show performance statistics with better styling"""
        stats = get_results_summary(self.conn)
        if not stats:
            messagebox.showinfo("Statistics", "No quiz results found yet.")
            return
            
        dialog = self.create_dialog("Quiz Statistics", 700, 600)

        # Header
        tk.Label(
            dialog,
            text="📊 Performance Statistics",
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary'],
            font=(self.font_family, 18, 'bold')
        ).pack(pady=(20, 30))

        # Overall stats card
        overall_card = tk.Frame(dialog, bg=self.colors['bg_secondary'], relief='flat')
        overall_card.pack(fill='x', padx=30, pady=(0, 20))

        tk.Label(
            overall_card,
            text="Overall Performance",
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary'],
            font=(self.font_family, 14, 'bold')
        ).pack(pady=(15, 10))

        total_questions = stats['total_questions']
        correct_answers = stats['correct_answers']
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        # Stats display
        stats_frame = tk.Frame(overall_card, bg=self.colors['bg_secondary'])
        stats_frame.pack(pady=(0, 15))

        # Create stats grid
        tk.Label(
            stats_frame,
            text=f"Questions Answered: {total_questions}",
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary'],
            font=(self.font_family, 12)
        ).grid(row=0, column=0, padx=20, pady=5, sticky='w')

        tk.Label(
            stats_frame,
            text=f"Correct Answers: {correct_answers}",
            fg=self.colors['success'],
            bg=self.colors['bg_secondary'],
            font=(self.font_family, 12, 'bold')
        ).grid(row=0, column=1, padx=20, pady=5, sticky='w')

        accuracy_color = self.colors['success'] if accuracy >= 70 else self.colors['warning']
        tk.Label(
            stats_frame,
            text=f"Accuracy: {accuracy:.1f}%",
            fg=accuracy_color,
            bg=self.colors['bg_secondary'],
            font=(self.font_family, 14, 'bold')
        ).grid(row=1, column=0, columnspan=2, pady=10)

        # Domain stats
        domain_card = tk.Frame(dialog, bg=self.colors['bg_secondary'], relief='flat')
        domain_card.pack(fill='both', expand=True, padx=30, pady=(0, 30))

        tk.Label(
            domain_card,
            text="Performance by Domain",
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary'],
            font=(self.font_family, 14, 'bold')
        ).pack(pady=(15, 10))

        # Domain stats in a nice scrollable list
        text_widget = tk.Text(
            domain_card,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            font=(self.mono_font, 11),
            wrap='none',
            padx=15,
            pady=15
        )
        domain_scrollbar = tk.Scrollbar(domain_card, command=text_widget.yview)
        text_widget.config(yscrollcommand=domain_scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=(0, 15))
        domain_scrollbar.pack(side='right', fill='y', padx=(0, 15), pady=(0, 15))

        for domain_stat in stats['domain_stats']:
            domain = domain_stat['domain']
            total = domain_stat['total']
            correct = domain_stat['correct']
            acc = (correct / total * 100) if total > 0 else 0
            
            # Format domain stats nicely
            text_widget.insert('end', f"📁 {domain}\n")
            text_widget.insert('end', f"   Questions: {total:2d} | Correct: {correct:2d} | Accuracy: {acc:5.1f}%\n\n")

        text_widget.config(state='disabled')

    def clear_frame(self):
        for w in self.frame_choices.winfo_children():
            w.destroy()

    def show_question(self):
        self.clear_frame()
        if self.index < 0 or self.index >= len(self.questions):
            if self.quiz_mode == 'normal':
                messagebox.showinfo('🎉 Quiz Complete', f'Great job! You completed {len(self.questions)} questions.\n\nCheck your statistics for performance details.')
            else:
                messagebox.showinfo('📚 Review Complete', f'Review session finished!\n\nYou reviewed {len(self.questions)} questions.')
            return

        q = self.questions[self.index]
        
        # Update progress
        progress = ((self.index + 1) / len(self.questions)) * 100
        self.progress_var.set(progress)
        
        # Update info label
        mode_text = f"[{self.quiz_mode.title()}] " if self.quiz_mode != 'normal' else ""
        self.lbl_info.config(
            text=f"{mode_text}Question {self.index + 1} of {len(self.questions)} • {q.domain}"
        )
        
        self.txt_question.config(text=q.text)
        
        fav = is_favorite(self.conn, q.id)
        self.btn_fav.config(text='★ Unfavorite' if fav else '☆ Favorite')
        
        if q.type == 'mcq':
            self.user_answer = tk.StringVar()
            for i, choice in enumerate(q.choices):
                choice_frame = tk.Frame(self.frame_choices, bg=self.colors['bg_secondary'])
                choice_frame.pack(fill='x', pady=8, padx=20)
                
                rb = tk.Radiobutton(
                    choice_frame,
                    text=f"  {chr(65+i)}. {choice}",
                    variable=self.user_answer,
                    value=choice,
                    fg=self.colors['text_primary'],  
                    bg=self.colors['bg_secondary'],
                    selectcolor=self.colors['accent'],
                    font=(self.font_family, 12),
                    anchor='w',
                    pady=12,
                    padx=15
                )
                rb.pack(fill='x')
                
        elif q.type == 'ordering':
            self.order_items = list(q.choices)
            
            tk.Label(
                self.frame_choices,
                text="💡 Drag items to reorder them (click and drag):",
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_primary'],
                font=(self.font_family, 11)
            ).pack(anchor='w', padx=20, pady=(0, 15))
            
            listbox_frame = tk.Frame(self.frame_choices, bg=self.colors['bg_primary'])
            listbox_frame.pack(fill='both', expand=True, padx=20)
            
            self.lb = tk.Listbox(
                listbox_frame,
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                selectbackground=self.colors['accent'],
                font=(self.font_family, 12),
                height=min(len(self.order_items), 8),
                relief='flat',
                bd=1
            )
            for item in self.order_items:
                self.lb.insert('end', f"   {item}")
            self.lb.bind('<B1-Motion>', self.on_drag)
            self.lb.pack(fill='both', expand=True)
            
        self.btn_next.config(text='Submit Answer' if self.btn_next['text'] != 'Next →' else 'Submit Answer')
        self.btn_next.config(command=self.submit_answer)
        self.btn_prev.config(state='normal' if self.index > 0 else 'disabled')

    def on_drag(self, event):
        lb = self.lb
        i = lb.nearest(event.y)
        if i < 0:
            return
        lb.selection_clear(0, 'end')
        lb.selection_set(i)
        lb.activate(i)
        if event.y < 0:
            return
        lb_index = lb.nearest(event.y)
        if lb_index != i:
            item = lb.get(i)
            lb.delete(i)
            lb.insert(lb_index, item)

    def submit_answer(self):
        q = self.questions[self.index]
        if q.type == 'mcq':
            answer = self.user_answer.get()
            if not answer:
                messagebox.showwarning('Warning', 'Please select an answer first!')
                return
            correct = (answer == q.answer)
        else:
            # Clean the ordering answer (remove the leading spaces)
            answer = [item.strip() for item in self.lb.get(0, 'end')]
            correct = (answer == q.answer)
            
        save_result(self.conn, q.id, json.dumps(answer), json.dumps(q.answer), correct, q.domain)
        
        result_text = '✅ Correct!' if correct else f'❌ Incorrect\n\nCorrect answer: {q.answer}'
        if hasattr(q, 'explanation') and q.explanation:
            result_text += f'\n\n💡 Explanation:\n{q.explanation}'
            
        messagebox.showinfo('Result', result_text)
        self.btn_next.config(text='Next Question →', command=self.next_question)

    def submit_or_next(self):
        """Handle Enter key - submit or go to next question"""
        if 'Submit' in self.btn_next['text']:
            self.submit_answer()
        else:
            self.next_question()

    def next_question(self):
        self.index += 1
        if self.index >= len(self.questions):
            if self.quiz_mode == 'normal':
                messagebox.showinfo('🎉 Quiz Complete', f'Great job! You completed {len(self.questions)} questions.\n\nCheck your statistics for performance details.')
            else:
                messagebox.showinfo('📚 Review Complete', f'Review session finished!\n\nYou reviewed {len(self.questions)} questions.')
            self.show_domain_selection()
            return
        self.show_question()

    def prev_question(self):
        if self.index > 0:
            self.index -= 1
            self.show_question()

    def toggle_fav(self):
        q = self.questions[self.index]
        fav = is_favorite(self.conn, q.id)
        mark_favorite(self.conn, q.id, not fav)
        self.btn_fav.config(text='★ Unfavorite' if not fav else '☆ Favorite')

    def explain(self):
        if not self.model:
            messagebox.showwarning('⚠️ AI Unavailable', 'No Ollama model available for explanations.\n\nMake sure Ollama is running and has models installed.')
            return
            
        q = self.questions[self.index]
        prompt = (
            "You are a CISSP expert tutor. Provide a clear, concise explanation for this question. "
            "Explain why the correct answer is right and why other options are wrong. "
            "Keep it educational and focused on CISSP concepts.\n\n"
            f"Question: {q.text}\n"
            f"Choices: {', '.join(q.choices)}\n"
            f"Correct Answer: {q.answer}"
        )
        
        # Show loading dialog
        loading_dialog = self.create_dialog("Generating Explanation...", 400, 150)
        loading_dialog.resizable(False, False)
        
        tk.Label(
            loading_dialog,
            text="🤖 Requesting explanation from AI...\n\nThis may take a moment.",
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary'],
            font=(self.font_family, 12),
            justify='center'
        ).pack(expand=True)
        
        loading_dialog.update()
        
        try:
            resp = ask_model(self.model, prompt)
            loading_dialog.destroy()
            
            # Show explanation dialog
            exp_dialog = self.create_dialog("AI Explanation", 800, 600)
            
            # Header
            tk.Label(
                exp_dialog,
                text=f"💡 Explanation: {q.text[:80]}...",
                fg=self.colors['text_primary'],
                bg=self.colors['bg_primary'],
                font=(self.font_family, 14, 'bold'),
                wraplength=750
            ).pack(pady=(20, 15))
            
            # Explanation text
            text_frame = tk.Frame(exp_dialog, bg=self.colors['bg_primary'])
            text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            text_widget = tk.Text(
                text_frame,
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=(self.font_family, 12),
                wrap='word',
                padx=20,
                pady=20,
                relief='flat'
            )
            text_scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
            text_widget.config(yscrollcommand=text_scrollbar.set)
            
            text_widget.pack(side='left', fill='both', expand=True)
            text_scrollbar.pack(side='right', fill='y')
            
            text_widget.insert('1.0', resp)
            text_widget.config(state='disabled')
            
        except Exception as e:
            loading_dialog.destroy()
            messagebox.showerror('❌ Error', f'Failed to get explanation:\n\n{str(e)}')
