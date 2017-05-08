#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy_communication import *
from text_handling.text_handling import *


class ZeroScreen(Screen):
    pass


class EndScreen(Screen):
    pass


class QuestionScreen(Screen):
    current_question = 0
    next_question = 0
    the_text = None
    the_image = None
    exp_name = None

    def on_pre_enter(self, *args):
        # self.update_question()
        pass

    def on_enter(self, *args):
        if self.the_text:
            TTS.speak([self.the_text], finished=self.update_question)

    def update_question(self, current_question=None):
        KL.log.insert(action=LogAction.data, obj=self.the_image, comment='present_time')
        self.ids['image_id'].source = 'images/' + self.exp_name + ' Pic/' + str(self.the_image)

        self.ids['yes_button'].name = str(self.the_image) + '_yes'
        self.ids['no_button'].name = str(self.the_image) + '_no'

    def pressed(self, answer):
        print(answer)
        if self.next_question > 0:
            next_screen = self.exp_name + '_question_screen_' + str(self.next_question)
            self.manager.current = next_screen
        else:
            self.manager.current = 'end_screen'


class EmbodimentApp(App):
    q_dict = {}

    def build(self):
        self.load_questions()
        self.init_communication()

        TTS.start()
        self.sm = ScreenManager()

        self.zero_screen = ZeroScreen(name='zero_screen')
        self.zero_screen.ids['subject_id'].bind(text=self.zero_screen.ids['subject_id'].on_text_change)
        self.sm.add_widget(self.zero_screen)

        self.questions = []
        i_question = 0
        for exp_name, questions in self.q_dict.items():
            for q_number, q_data in questions.items():
                self.questions.append(QuestionScreen(name=exp_name + '_question_screen_' + q_number))
                self.questions[-1].exp_name = exp_name
                self.questions[-1].the_text = q_data['text']
                self.questions[-1].the_image = q_data['image']
                self.questions[-1].current_question = int(q_number)
                if self.questions[-1].current_question < len(questions):
                    self.questions[-1].next_question = int(q_number) + 1
                else:
                    self.questions[-1].next_question = -1
                self.sm.add_widget(self.questions[-1])
                i_question += 1


        self.end_screen = EndScreen(name='end_screen')
        self.sm.add_widget(self.end_screen)

        self.sm.current = 'zero_screen'
        return self.sm

    def load_questions(self):
        self.q_dict = json.load(open('images/questions.json'))

    def init_communication(self):
        KC.start(the_ip='192.168.1.254', the_parents=[self])  # 127.0.0.1
        KL.start(mode=[DataMode.file, DataMode.communication, DataMode.ros], pathname=self.user_data_dir,
                 the_ip='192.168.1.254')

    def on_connection(self):
        KL.log.insert(action=LogAction.data, obj='SpatialSkillAssessmentApp', comment='start')

    def press_start(self, exp_name):
        self.sm.current = exp_name + '_question_screen_1'

    def end_game(self):
        self.stop()

if __name__ == '__main__':
    EmbodimentApp().run()
