from ConsoleListInterface import waitForEnter, cls
import os


HOMEPATH = os.path.dirname(os.path.realpath(__file__))

def main():
    skip_phases = input("Skip phases: ")
    skip_phases = skip_phases.split()

    print()
    
    os.chdir("python pipeline")
    for file in zip(os.listdir(f"{HOMEPATH}/python pipeline"), ["1. Extracting and cleaning concepts", "2. Calculating co-occurence", "3. Splitting concepts by first letter", "4. Merging sub-concepts into primary concepts"]):
        if any(file[1].startswith(phase) for phase in skip_phases):
            continue
        print(f"{file[1]}:\n")
        os.system(f'python3 {file[0]}')
        print("\nEnter to continue.")
        waitForEnter()
        cls()


if __name__=="__main__":
    main()