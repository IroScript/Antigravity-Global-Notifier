import shlex
import re

def check_destructive(command_str):
    # Check specific destructive sub-commands and flags
    if re.search(r'find\b.*(?:\s+-(?:delete|exec\s+rm))', command_str):
        return True, 'Destructive find command (-delete / -exec rm)'
    if re.search(r'git\s+clean\b', command_str):
        return True, 'Destructive git clean command'
    if re.search(r'git\s+reset\s+--hard\b', command_str):
        return True, 'Destructive git reset --hard command'
    if re.search(r'git\s+checkout\s+--', command_str):
        return True, 'Destructive git checkout -- file revert'
    if re.search(r'git\s+restore\b', command_str):
        return True, 'Destructive git restore command'
    if re.search(r'rsync\b.*--delete', command_str):
        return True, 'Destructive rsync --delete command'
    
    # Redirection truncation to non-null target: > target or >> target (if destructive)
    redirs = re.findall(r'>\s*([^&|0-9\s]+)', command_str)
    for t in redirs:
        if t not in ['/dev/null', '&1', '&2']:
            return True, f'Destructive shell truncation into {t}'

    if re.search(r'chattr\s+-[a-zA-Z]*i', command_str):
        return True, 'Stripping immutable attribute (+i -> -i)'
    if re.search(r'os\.(?:remove|unlink|rmdir)\(', command_str):
        return True, 'Python os removal call'
    if re.search(r'shutil\.rmtree\(', command_str):
        return True, 'Python shutil.rmtree call'
    if re.search(r'Path\(.*\)\.(?:unlink|rmdir)\(', command_str):
        return True, 'Python Pathlib removal call'

    # Split commands by shell separators: ;, &&, ||, |, \n, $(), ``
    clean_str = re.sub(r'["\'].*?["\']', '', command_str) # strip quoted string contents for tokenizer
    segments = re.split(r'[;&|\n`$()]', clean_str)
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        try:
            tokens = shlex.split(seg)
        except Exception:
            tokens = seg.split()
        if not tokens:
            continue
        cmd = tokens[0]
        cmd_base = cmd.split('/')[-1]
        if cmd_base in ['rm', 'rmdir', 'unlink']:
            return True, f'Destructive file removal command ({cmd_base})'
        if cmd_base in ['truncate', 'fallocate']:
            return True, f'Destructive file truncation command ({cmd_base})'
        if cmd_base in ['sudo', 'su', 'pkexec', 'doas']:
            return True, f'Privilege escalation command ({cmd_base})'
        if cmd_base == 'xargs' and any(t.split('/')[-1] == 'rm' for t in tokens):
            return True, 'Indirect deletion via xargs rm'

    return False, 'Safe'

if __name__ == "__main__":
    test_cases = [
        'rm -rf /tmp/foo',
        'rm file.txt',
        'unlink file.txt',
        'rmdir somedir',
        '/bin/rm -f test',
        'find . -name "*.tmp" -delete',
        'find . -exec rm -f {} +',
        'xargs rm -f',
        'git clean -fd',
        'git clean -fdx',
        'git reset --hard HEAD~1',
        'git checkout -- .',
        'git restore .',
        'rsync -av --delete /src/ /dst/',
        'echo "" > /etc/passwd',
        'truncate -s 0 file.txt',
        'chattr -i /home/azureuser/POLICIES/safety_levels.json',
        'sudo whoami',
        'python3 -c "import os; os.remove(\\"foo\\")"',
        'python3 -c "import shutil; shutil.rmtree(\\"foo\\")"',
        'ls -la; rm -rf /',
        'echo hello && find . -delete',
        'git status', # safe
        'cargo test', # safe
        'echo "this mentions rm in text" > /dev/null', # safe
        'grep -r "rm" /tmp/dir' # safe
    ]

    for cmd in test_cases:
        is_dest, reason = check_destructive(cmd)
        res_str = 'DENIED' if is_dest else 'ALLOWED'
        print(f'[{res_str:7}] {cmd} -> {reason}')
