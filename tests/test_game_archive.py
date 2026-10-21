"""Security and path checks that run without distributing original game files."""
import io
from pathlib import Path
import stat
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from game_archive import _archive_entries, inspect_archive


def archive_with(*entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as zip_out:
        for name, content in entries:
            zip_out.writestr(name, content)
    stream.seek(0)
    return zipfile.ZipFile(stream)


class TestGameArchive(unittest.TestCase):
    def test_traversal_refused(self):
        with archive_with(('../outside', b'bad')) as archive:
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                _archive_entries(archive)

    def test_windows_absolute_refused(self):
        with archive_with(('C:/windows/notepad.exe', b'bad')) as archive:
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                _archive_entries(archive)

    def test_backslashes_refused(self):
        with archive_with(('PLACES\\P1\\MEGAFILE.HYP', b'bad')) as archive:
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                _archive_entries(archive)

    def test_case_insensitive_collision_refused(self):
        with archive_with(('PLACES/GAMEDATA', b'a'), ('places/gamedata', b'b')) as archive:
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                _archive_entries(archive)

    def test_symlink_refused(self):
        stream = io.BytesIO()
        entry = zipfile.ZipInfo('PLACES/link')
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr(entry, 'outside')
        stream.seek(0)
        with zipfile.ZipFile(stream) as archive:
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                _archive_entries(archive)

    def test_missing_game_data_refused(self):
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            inspect_archive(io.BytesIO(make_zip([('other.txt', b'foo')])))

    def test_safe_files_indexed(self):
        with archive_with(('PLACES/P1/MEGAFILE.HYP', b'123'), ('SOUNDS/S0.WAV', b'foo')) as archive:
            files, total = _archive_entries(archive)
            self.assertEqual(len(files), 2)
            self.assertEqual(total, 6)


def make_zip(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, contents in entries:
            archive.writestr(name, contents)
    return stream.getvalue()


if __name__ == '__main__':
    unittest.main()
