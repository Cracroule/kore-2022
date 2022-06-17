from kaggle_environments import make

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

    env = make("kore_fleets", debug=True)
    print(env.name, env.version)

    # env.run(["/kaggle/working/do_nothing.py"])
    env.run(["do_nothing.py"])
    env.render(mode="ipython", width=1000, height=800)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
