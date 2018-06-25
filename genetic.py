from tkinter import *

def center_position(width, height, root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)

    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def show(entries, root, outputtext):
    # go through the entries
    for entry in entries:
        field = entry[0]
        value  = entry[1].get()
        textval = ('%s: "%s"\n' % (field, value))
        print('%s: "%s"' % (field, value))
        outputtext.insert(END, textval)
    # populate text display element
    outputtext.place(x=30, y=200)

def formsetup(root, fields):
    # value to be returned
    entries = []

    # username elements creation
    txt_username = StringVar()
    label_username = Label(root, text="Username:").place(x=30, y=30)
    entry_username = Entry(root, textvariable=txt_username).place(x=130, y=30)
    entries.append((fields[0], txt_username))

    # password elements creation
    txt_password = StringVar()
    label_password = Label(root, text="Password:").place(x=30, y=60)
    entry_password = Entry(root, show="*", textvariable=txt_password).place(x=130, y=60)
    entries.append((fields[1], txt_password))

    # course elements creation
    list_course = ['BCT','BCC','EC','EB','EM','BB','MC']
    txt_course = StringVar()
    txt_course.set("BCT")
    label_course = Label(root, text="Intended Course:").place(x=30, y=90)
    droplist_course = OptionMenu(root, txt_course, *list_course).place(x=130, y=90)
    entries.append((fields[2], txt_course))

    # term elements creation
    txt_term = StringVar()
    label_term = Label(root, text="Acedemic Term:").place(x=270, y=30)
    entry_term = Entry(root, textvariable=txt_term).place(x=370, y=30)
    entries.append((fields[3], txt_term))

    # preference elements creation
    list_pref = ['NOTURNO','INTEGRAL']
    txt_pref = StringVar()
    txt_pref.set("NOTURNO")
    label_pref = Label(root, text="Preference:").place(x=270, y=60)
    droplist_pref = OptionMenu(root, txt_pref, *list_pref).place(x=370, y=60)
    entries.append((fields[4], txt_pref))

    # time preference elements creation
    # txt_time = StringVar()
    # label_time = Label(root, text="Preference:").place(x=400, y=60)
    # listbox_time = Listbox(root, selectmode=MULTIPLE)
    # listbox_time.insert(END, "8:00-10:00")
    # listbox_time.insert(END, "10:00-12:00")
    # listbox_time.insert(END, "13:30-15:30")
    # listbox_time.insert(END, "19:00-21:00")
    # listbox_time.insert(END, "21:00-23:00")
    # listbox_time.place(x=470, y=60)
    # selected = listbox_time.curselection()
    # str_sel = ""
    # for sel in selected:
    #     str_sel += sel
    # print(str_sel)
    # txt_time = str_sel
    # entries.append((fields[5], txt_time))

    return entries

def check_expression(root, entries):

    for entry in entries:
        field = entry[0]
        value  = entry[1].get()
        # textval += ('%s: "%s"' % (field, value))
        outputtext.insert(END, value)
    outputtext.place(x=150, y=200)

def main():
    # window creation and title definition
    root = Tk()
    root.title("Genetic Algorithm - Course Matrix Generator")
    # sets to center position
    center_position(700, 650, root)

    # fields to be received as inputs
    fields = 'Username', 'Password', 'Course', 'Academic Term', 'Preference', 'Time Preference'
    # form setup
    entries = formsetup(root, fields)
    # display text element
    outputtext = Text(root)

    # buttons setup
    btn_start = Button(root, text='Start', width=12, command=(lambda e=entries: show(e, root, outputtext))).place(x=30, y=150)
    btn_leave = Button(root, text='Quit', width=12, command=root.quit).place(x=150, y=150)

    root.mainloop()

if __name__ == '__main__':
    main()
