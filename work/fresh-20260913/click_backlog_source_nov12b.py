"""Keep the batch fix unchanged;avoid a forbidden C-library macro in the observer name."""
from click_backlog_source_nov12 import baseline as original_baseline, production as original


def fix(cpp, header):
    assert cpp.count('BatchEvents exit(_clockPaused);') == 1
    cpp = cpp.replace('BatchEvents exit(_clockPaused);', 'BatchEvents quitEvents(_clockPaused);')
    cpp = cpp.replace('exit.click(', 'quitEvents.click(').replace('exit.events.', 'quitEvents.events.')
    cpp = cpp.replace('&exit,false', '&quitEvents,false').replace('&exit);', '&quitEvents);')
    return cpp, header


def baseline(cpp, header):
    return fix(*original_baseline(cpp, header))


def production(cpp, header):
    return fix(*original(cpp, header))
