import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List
import json

from .data import Question
from .db import save_result, is_favorite, mark_favorite
from .ollama import ask_model


class QuizUI:
    def __init__(self, root: tk.Tk, questions: List[Question], conn, model: str):
        self.root = root
        self.questions = questions
        random.shuffle(self.questions)
        self.conn = conn
        self.model = model
        self.index = 0
        self.user_answer = None
        self.order_items = []
        self.build_ui()
        self.show_question()

    def build_ui(self):
        self.root.title('CISSP Quiz')
        self.root.configure(bg='#222')
        self.root.bind('<Left>', lambda e: self.prev_question())
        self.root.bind('<Right>', lambda e: self.next_question())

        self.lbl_domain = tk.Label(self.root, text='', fg='white', bg='#222')
        self.lbl_domain.pack(pady=5)

        self.txt_question = tk.Label(self.root, text='', wraplength=600, fg='white', bg='#222')
        self.txt_question.pack(pady=10)

        self.frame_choices = tk.Frame(self.root, bg='#222')
        self.frame_choices.pack(pady=5)

        self.btn_explain = tk.Button(self.root, text='Explain', command=self.explain)
        self.btn_explain.pack(pady=5)

        self.btn_fav = tk.Button(self.root, text='Favorite', command=self.toggle_fav)
        self.btn_fav.pack(pady=5)

        self.btn_next = tk.Button(self.root, text='Next', command=self.next_question)
        self.btn_next.pack(pady=10)

    def clear_frame(self):
        for w in self.frame_choices.winfo_children():
            w.destroy()

    def show_question(self):
        self.clear_frame()
        if self.index < 0 or self.index >= len(self.questions):
            messagebox.showinfo('End', 'No more questions.')
            return
        q = self.questions[self.index]
        self.lbl_domain.config(text=q.domain)
        self.txt_question.config(text=q.text)
        fav = is_favorite(self.conn, q.id)
        self.btn_fav.config(text='Unfavorite' if fav else 'Favorite')
        if q.type == 'mcq':
            self.user_answer = tk.StringVar()
            for choice in q.choices:
                rb = tk.Radiobutton(
                    self.frame_choices,
                    text=choice,
                    variable=self.user_answer,
                    value=choice,
                    fg='white',
                    bg='#222',
                    selectcolor='#444')
                rb.pack(anchor='w')
        elif q.type == 'ordering':
            self.order_items = list(q.choices)
            self.lb = tk.Listbox(self.frame_choices)
            for item in self.order_items:
                self.lb.insert('end', item)
            self.lb.bind('<B1-Motion>', self.on_drag)
            self.lb.pack()
        self.btn_next.config(text='Submit', command=self.submit_answer)

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
                messagebox.showwarning('Warning', 'Select an answer')
                return
            correct = (answer == q.answer)
        else:
            answer = list(self.lb.get(0, 'end'))
            correct = (answer == q.answer)
        save_result(self.conn, q.id, json.dumps(answer), json.dumps(q.answer), correct, q.domain)
        messagebox.showinfo('Result', 'Correct!' if correct else f'Incorrect. Answer: {q.answer}')
        self.btn_next.config(text='Next', command=self.next_question)

    def next_question(self):
        self.index += 1
        if self.index >= len(self.questions):
            messagebox.showinfo('End', 'Quiz finished!')
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
        self.btn_fav.config(text='Unfavorite' if not fav else 'Favorite')

    def explain(self):
        q = self.questions[self.index]
        prompt = (
            "You are a CISSP tutor. Paraphrase the question, explain why the correct"
            " answer is correct from the CISSP perspective."
            f"\nQuestion: {q.text}\nChoices: {q.choices}\nCorrect Answer: {q.answer}"
        )
        resp = ask_model(self.model, prompt)
        messagebox.showinfo('Explanation', resp)
