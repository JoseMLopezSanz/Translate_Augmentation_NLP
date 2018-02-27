from textblob import TextBlob
from textblob.translate import NotTranslated
import pandas as pd
import os
import progressbar
import sys


class Aug_Translation():
    def __init__(self, comments, language="es", orig_language="en", labels=None, classes=None, output_path="translated.csv", num_translations=1):
        self.comments = comments
        self.language = language
        self.labels = labels 
        self.classes = classes
        self.num_classes = len(classes)
        self.output_path = output_path
        self.num_translations = num_translations
        self.orig_language = orig_language
        
        self.columns = ["Comments"] + self.classes + ["Translated"]
        self.language_dict = {"Afrikaans" : "af","Albanian" : "sq","Amharic" : "am","Arabic" : "ar","Armenian" : "hy",
                                "Azeerbaijani" : "az","Basque" : "eu","Bengali" : "bn","Bosnian" : "bs", 
                                "Bulgarian" : "bg","Catalan" : "ca","Cebuano" : "ceb","Chinese (Simplified)" : "zh-CN",
                                "Chinese (Traditional)" : "zh-TW","Corsican" : "co","Croatian" : "hr","Czech" : "cs",
                                "Danish" : "da","Dutch" : "nl","Esperanto" : "eo","Estonian" : "et","Finnish" : "fi",
                                "French" : "fr","Frisian" : "fy","Galician" : "gl","Georgian" : "ka","German" : "de",
                                "Greek" : "el","Gujarati" : "gu","Haitian Creole" : "ht","Hausa" : "ha","Hawaiian" : "haw",
                                "Hebrew" : "iw","Hindi" : "hi","Hmong" : "hmn","Hungarian" : "hu","Icelandic" : "is",
                                "Igbo" : "ig","Indonesian" : "id","Irish" : "ga","Italian" : "it","Japanese" : "ja",
                                "Javanese" : "jw","Kannada" : "kn","Kazakh" : "kk","Khmer" : "km","Korean" : "ko",
                                "Kurdish" : "ku","Lao" : "lo","Latvian" : "lv","Lithuanian" : "lt","Luxembourgish" : "lb",
                                "Macedonian" : "mk","Malagasy" : "mg","Malay" : "ms","Malayalam" : "ml","Maltese" : "mt",
                                "Maori" : "mi","Marathi" : "mr","Mongolian" : "mn","Nepali" : "ne","Norwegian" : "no",
                                "Nyanja (Chichewa)" : "ny","Pashto" : "ps","Persian" : "fa","Polish" : "pl",
                                "Portuguese (Portugal, Brazil)" : "pt","Punjabi" : "pa","Romanian" : "ro","Russian" : "ru",
                                "Samoan" : "sm","Scots Gaelic" : "gd","Serbian" : "sr","Sesotho" : "st","Shona" : "sn",
                                "Sindhi" : "sd","Sinhala (Sinhalese)" : "si","Slovak" : "sk","Slovenian" : "sl",
                                "Somali" : "so","Spanish" : "es","Swahili" : "sw","Swedish" : "sv","Tagalog (Filipino)" : "tl",
                                "Tajik" : "tg","Tamil" : "ta","Telugu" : "te","Thai" : "th","Turkish" : "tr","Ukrainian" : "uk",
                                "Urdu" : "ur","Uzbek" : "uz","Vietnamese" : "vi","Welsh" : "cy","Xhosa" : "xh",
                                "Yiddish" : "yi","Yoruba" : "yo","Zulu" : "zu"}
        
    def print_dictionary(self, like=None):
        """Prints dictionary of languages
            If line is None, it prints all languages
            if like is a string then prints similar languages 
        """
        try:
            for i in self.language_dict:
                if  (like == None) or (like in i or like in self.language_dict[i]):
                    print("{} ---> {}".format(i, self.language_dict[i]))
        except ValueError:
            print("[ERROR] {}". format(ValueError))
    
    def create_output_csv(self):
        if os.path.isfile(self.output_path):
            self.df = pd.read_csv(self.output_path)
            match_comments = True
            #Check columns
            try:
                match = [0 for i, j in zip(self.df.columns, self.columns) if i == j]
                if sum(match) != 0:
                    print(self.df.columns)
                    print("[ERROR] The output file already exists but it doesn't have the right format")
                    print("[SOLUTION] Remove the output file or select a different output path")
                else:
                    #check that comments are the same
                    for i, comment in enumerate(self.df["Comments"]):
                        if self.df["Comments"][i] == comment:
                            next
                        else:
                            match_comments = False
                            break
                    if match_comments:   
                        print("[INFO] CSV loaded")
                        self.translated_comments=self.df["Translated"]
                    else:
                        print("[ERROR] The output file already exists but cooments don't match")
                        print("[SOLUTION] Remove the output file or select a different output path")
            except: 
                raise
                print("[ERROR] The output file already exists but it doesn't have the right format")
                print("[SOLUTION] Remove the output file or select a different output path")
        else:
            comments = pd.DataFrame(self.comments)
            if self.labels is not None:
                labels = pd.DataFrame(self.labels)
            self.df = pd.concat([comments, labels], axis=1)
            self.df["Translated"] = "Untranslated"
            columns = self.columns
            self.df.columns = columns
            self.df.to_csv(self.output_path, index=False)
            self.translated_comments=self.df["Translated"]
            print("[INFO] CSV succesfully created")
     
    def translate_single_doc(self, comment, language):
        if hasattr(comment, "decode"):
            comment = comment.decode("utf-8")

        text = TextBlob(comment)
        try:
            text = text.translate(to=language)
            text = text.translate(to=self.orig_language)
        except NotTranslated:
            pass

        return str(text)
    
    def translate_all_docs(self):
        #tranlated_comments = [translate(comment, "es") for comment in comments]
        total_comments = len(self.df["Comments"])
        first_trasnlation = False
        save_csv = 500
        widgets = ["Translating: ", progressbar.Counter(),"/{}".format(total_comments) , progressbar.Percentage(),
                   " ", progressbar.Bar(), " ", progressbar.AdaptiveETA(),
                  " Saved comment: ", progressbar.FormatLabel(' ')]
        pbar = progressbar.ProgressBar(maxval=total_comments, widgets=widgets).start()
    
        for i, comment in enumerate(self.df["Comments"]):
            if self.df["Translated"][i] == "Untranslated":
                first_trasnlation = True
                #print("{}/{}".format(i+1,total))
                #print(comment)
                for num_t in range(self.num_translations):
                    comment = self.translate_single_doc(comment, self.language)
                #print(comment_trans)
                self.translated_comments[i] = comment
            if i % save_csv == 0 and first_trasnlation:
                self.save()
                widgets[9] = progressbar.FormatLabel('{0}'.format(i))
            pbar.update(i)
            
    def translate(self):
        self.create_output_csv()
        sys.stdout.flush()
        self.translate_all_docs()
        print("Finished")
        
    def save(self):
        self.df.to_csv(self.output_path, index=False)
        
        
