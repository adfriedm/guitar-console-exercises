import random
from collections import defaultdict
from enum import Enum

degree_frets_lu = {
    '1':  [(1,5), (3,3), (1,0)],
    'b2': [(2,5), (4,3), (2,0)],
    '2':  [(3,5), (0,2), (3,0)],
    'b3': [(4,5), (1,2), (4,0)],
    '3':  [(0,4), (2,2)],
    '4':  [(1,4), (3,2)],
    '#4': [(2,4), (4,2)],
    'b5': [(2,4), (4,2)],
    '5':  [(3,4), (1,1)],
    'b6': [(4,4), (2,1)],
    '6':  [(0,3), (3,1)],
    'b7': [(1,3), (4,1)],
    '7':  [(2,3), (0,0)] }

mode_degrees_lu = {
    'lydian':     ['1', '2', '3', '#4', '5', '6', '7'],
    'ionian':     ['1', '2', '3', '4', '5', '6', '7'],
    'mixolydian': ['1', '2', '3', '4', '5', '6', 'b7'],
    'dorian':     ['1', '2', 'b3', '4', '5', '6', 'b7'],
    'aeolian':    ['1', '2', 'b3', '4', '5', 'b6', 'b7'],
    'phrygian':   ['1', 'b2', 'b3', '4', '5', 'b6', 'b7'],
    'locrian':    ['1', 'b2', 'b3', '4', 'b5', 'b6', 'b7'] }

# Store the mode names
modes = mode_degrees_lu.keys()

# Defines some alternate forms of the mode names
mode_alts_lu = { mode: [mode[:short_len]
                 for short_len in xrange(2,4)]
                 for mode in modes }
# Add the names themselves
for mode in modes:
    mode_alts_lu[mode].append(mode)
     
def degrees2mode_QA(sub_modes=modes):
    cur_mode = random.choice(sub_modes)
    question = "What mode corresponds to {}? ".format(
                    " ".join(
                         mode_degrees_lu[cur_mode]
                    )
               ) 
    acceptable_answers = mode_alts_lu[cur_mode]
    best_answer = cur_mode
    return question, acceptable_answers, best_answer

    


         
class Fretboard:
    def __init__(self, frets, line_prefix=""):
        self.frets = frets
        self.line_prefix = line_prefix

    def __str__(self):
        diag = "\n".join( 
                    self.line_prefix + \
                    " | ".join(
                        'X' if (f,s) in self.frets else ' '
                        for f in xrange(6)
                     )
                    for s in xrange(6)
               )
        return diag
 

def fretboard2mode_QA(sub_modes=modes):
    cur_mode = random.choice(sub_modes)
    question = "What mode corresponds to \n{}\n? ".format(
            gen_mode_diag(cur_mode, line_prefix='\t'))
    acceptable_answers = mode_alts_lu[cur_mode]
    best_answer = cur_mode
    return question, acceptable_answers, best_answer




def gen_mode_diag(mode, line_prefix=""):
    frets = [fret for degree in mode_degrees_lu[mode]
                for fret in degree_frets_lu[degree]]
    #frets = [].join(degree_frets_lu[degree] for degree in
    #        mode_degrees_lu[mode])

    return Fretboard(frets, line_prefix=line_prefix)







class Quiz:
    def __init__(self, quiz_name, gen_QA, quiz_params=None, flags=['q','x','f']):
        self.name = quiz_name
        self.score = 0
        self.attempted = 0
        self.gen_QA = lambda: gen_QA(**quiz_params)
        self.flags = list(flags)
        self.results = []

    def __str__(self):
        return "{} score: {}/{} ({:.1%})".format(
                    self.name,
                    self.score,
                    self.attempted,
                    float(self.score)/self.attempted
                        if self.attempted != 0
                        else -float('inf')
                )

    # Bit of functional programming, cause why not?
    def ask_question(self):
        question, acceptable_answers, best_answer = self.gen_QA()
        user_input = raw_input(question)
    
        # flags are passed straight out
        if user_input in self.flags:
            return None, user_input

        ans_correct = user_input in acceptable_answers
        if ans_correct:
            self.score += 1
        # Could also append a timestamp, speed of response, etc
        self.results.append({'success': ans_correct,
                             'best_answer': best_answer})
        self.attempted += 1

        return self.results[-1], ""


class QuizRunner:
    class Status(Enum):
        welcome = 0
        quiz = 1
        menu = 2
        config = 3
        save = 4

    def __init__(self, quizzes):
        self.quizzes = quizzes
        self.current_quiz = None
        self.status = QuizRunner.Status.welcome

    def do_next(self):
        if self.status == QuizRunner.Status.welcome:
            print "Guitar Theory Exercises by adfriedman"
            self.status = QuizRunner.Status.menu
            return 1

        elif self.status == QuizRunner.Status.quiz:
            result, flag = self.current_quiz.ask_question()
            if flag == 'q':
                return 0
            elif flag == 'x':
                self.status = QuizRunner.Status.menu
                return 1
            elif flag == 'f':
                print self.current_quiz, "\n"
            else:
                print "{} ({})\n".format('yes' if result['success']
                        else 'no' , result['best_answer'])
            return 1

        elif self.status == QuizRunner.Status.menu:
            print "\nExercizes"
            for i,quiz in enumerate(self.quizzes):
                print "{}) {}".format(i+1, quiz.name)
            user_input = raw_input("Choose a program or type q to quit\n")
            if user_input == 'q':
                return 0
            
            try: 
                if 0 < int(user_input) <= len(self.quizzes):
                    self.current_quiz = self.quizzes[int(user_input)-1]
                    self.status = QuizRunner.Status.quiz
                    print "\nStarting {} Quiz".format(self.current_quiz.name)
                else:
                    raise ValueError
            except ValueError:
                print "Input not understood, please try again."

            return 1
            

    



if __name__ == "__main__":

    # Choose a subset of the modes
    sub_modes = modes[0:2]

    # Setup quizzes
    degrees2mode_quiz = Quiz("Degree2Mode",
            degrees2mode_QA, 
            {'sub_modes': sub_modes},
            flags=['q','x','f'])

    fretboard2mode_quiz = Quiz("Fretboard2Mode",
            fretboard2mode_QA, 
            {'sub_modes': sub_modes},
            flags=['q','x','f'])
    quiz_runner = QuizRunner([degrees2mode_quiz, fretboard2mode_quiz])

    while quiz_runner.do_next():
        pass
    else:
        print "Good Bye"



