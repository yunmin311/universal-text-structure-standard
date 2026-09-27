#!/usr/bin/env python3
"""Small Markdown gates; intentionally not a complete Markdown parser."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def registry_check(data=None):
    try:
        import yaml
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ValueError('Schema 检查需要 PyYAML 和 jsonschema；参见 README 安装命令') from exc
    if data is None:
        data = yaml.safe_load((ROOT / 'FORMAT_RULES.yaml').read_text(encoding='utf-8'))
    schema = json.loads((ROOT / 'schemas/format-rules.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(data))
    if errors:
        raise ValueError('; '.join(e.message for e in errors))
    ids = [r['rule_id'] for r in data['rules']]
    if len(set(ids)) != len(ids):
        raise ValueError('rule_id 必须唯一；JSON Schema 的 uniqueItems 不能保证对象某一字段唯一')
    mapped = set()
    for rule in data['rules']:
        for side, examples in rule['examples'].items():
            for example in examples:
                file = ROOT / example
                if not example.startswith(f'examples/{side}/') or '..' in Path(example).parts or not file.is_file():
                    raise ValueError(f'无效 example: {example}')
                header = re.match(r'<!-- rules: ([^;]+);', file.read_text(encoding='utf-8'))
                if not header or rule['rule_id'] not in header[1].split(', '):
                    raise ValueError(f'缺少反向规则映射: {example} / {rule["rule_id"]}')
                mapped.add(example)
        for source in rule['sources']:
            name, _, anchor = source.partition('#')
            file = ROOT / name
            if name != 'references/README.md' or not file.is_file():
                raise ValueError(f'缺失公开 source: {source}')
            if anchor and f'id="{anchor}"' not in file.read_text(encoding='utf-8'):
                raise ValueError(f'缺失 source anchor: {source}')
    for file in (ROOT / 'examples').rglob('*.md'):
        name = file.relative_to(ROOT).as_posix()
        if name not in mapped:
            raise ValueError(f'示例未登记: {name}')
        header = re.match(r'<!-- rules: ([^;]+);', file.read_text(encoding='utf-8'))
        if not header:
            raise ValueError(f'示例缺少 metadata: {name}')
        for rid in header[1].split(', '):
            match = next((r for r in data['rules'] if r['rule_id'] == rid), None)
            side = file.parent.name
            if not match or name not in match['examples'][side]:
                raise ValueError(f'示例反向映射未登记: {name} / {rid}')
    return data


def scan(text):
    findings = []
    def emit(rid, line, severity, message):
        item = dict(rule_id=rid, line=line, severity=severity, message=message)
        if not any(d['rule_id'] == rid and d['line'] == line for d in findings):
            findings.append(item)

    # Mask HTML comments, escaped punctuation and fenced blocks, preserving offsets.
    mask = lambda m: re.sub(r'[^\n]', ' ', m.group())
    text = re.sub(r'<!--[\s\S]*?-->', mask, text)
    lines = text.splitlines()
    visible = []
    fence = None
    previous_heading = 0
    blank_run = 0
    for number, raw in enumerate(lines, 1):
        if fence:
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}[ \t]*', raw):
                fence = None
            visible.append('')
            continue
        match = re.match(r' {0,3}(`{3,}|~{3,})(.*)$', raw)
        if match and not (match[1][0] == '`' and '`' in match[2]):
            fence = (match[1][0], len(match[1]), number)
            visible.append('')
            continue
        # Four-space indented code is ambiguous with list continuation; skip non-list text.
        if re.match(r'^(?: {4}|\t)', raw) and not re.match(r'^\s*(?:[-+*]|\d+[.)])\s', raw):
            visible.append('')
            continue
        line = re.sub(r'\\[!"#$%&\'()*+,\-./:;<=>?@\[\]\\^_`{|}~]', lambda m: '  ', raw)
        visible.append(line)
        blank_run = blank_run + 1 if not raw.strip() else 0
        if blank_run == 3:
            emit('PRE-003', number, 'WARNING', '连续空行；检查是否无必要留白')
        heading = re.match(r' {0,3}(#{1,6})\s+\S', line)
        if heading:
            level = len(heading[1])
            if previous_heading and level > previous_heading + 1:
                emit('SEM-005', number, 'WARNING', '标题向下跳级')
            previous_heading = level
        indent = re.match(r'^(\s*)(?:[-+*]|\d+[.)])\s', raw)
        if indent and len(indent[1].expandtabs(4)) >= 8:
            emit('REN-006', number, 'WARNING', '列表缩进至少 8 列；人工核对从属关系')
        if re.fullmatch(r'\s*\*\*[^*]+\*\*\s*', line):
            emit('PRE-004', number, 'WARNING', '独立粗体行可能是伪标题')

    if fence:
        emit('REN-003', fence[2], 'ERROR', '代码围栏未闭合')

    # Parse code spans within a paragraph, allowing multiline spans and variable delimiters.
    body = '\n'.join(visible)
    for number, line in enumerate(visible, 1):
        if re.match(r'^[ \t]*(?:(?:[-+*]|\d+[.)]) +)?\*\*(`+)[^`\n]+\1[:：]?\*\*', line):
            emit('REN-004', number, 'WARNING', '技术实体默认只用 inline code；合法嵌套需确认强调理由')
    for block in re.finditer(r'[^\n]+(?:\n(?!\n)[^\n]+)*', body):
        start_line = body.count('\n', 0, block.start()) + 1
        part = block.group()
        masked = list(part)
        pos = 0
        while pos < len(part):
            if part[pos] != '`':
                pos += 1
                continue
            run = re.match(r'`+', part[pos:])[0]
            end = re.search(r'(?<!`)' + re.escape(run) + r'(?!`)', part[pos + len(run):])
            number = start_line + part.count('\n', 0, pos)
            if end is None:
                emit('REN-002', number, 'ERROR', '行内代码未闭合（规范要求显式闭合）')
                pos += len(run)
                continue
            stop = pos + len(run) + end.end()
            content = part[pos + len(run):stop - len(run)]
            # A literal ** inside code is valid; flag only boundary-crossing or field context.
            stars = len(re.findall(r'(?<!\*)\*\*(?!\*)', content))
            suffix = part[stop:]
            if stars % 2 or (content.startswith('**') and content.endswith('**') and re.match(r'\*\*[:：]\*\*', suffix)):
                emit('REN-005', number, 'WARNING', '可疑粗体与代码交叉；检查字面内容是否为有意展示')
            for i in range(pos, stop):
                if masked[i] != '\n':
                    masked[i] = 'x'
            pos = stop
        plain = ''.join(masked)
        tokens = list(re.finditer(r'(?<!\*)\*\*(?!\*)', plain))
        if len(tokens) % 2:
            emit('REN-001', start_line + plain.count('\n', 0, tokens[-1].start()), 'ERROR', '双星号未成对')
        for match in re.finditer(r'\*\*[:：]\*\*|(?m:^[ \t]*(?:(?:[-+*]|\d+[.)]) +)?\*\*[^*\n]+\*\*[:：])', plain):
            emit('REN-004', start_line + plain.count('\n', 0, match.start()), 'WARNING', '字段冒号位于独立强调或强调外侧')

    def cells(line):
        # GFM pipes inside inline code still require escaping; escapes already masked.
        return [c.strip() for c in line.strip().strip('|').split('|')]
    i = 0
    while i < len(visible):
        if '|' not in visible[i]:
            i += 1
            continue
        j = i
        while j < len(visible) and '|' in visible[j]:
            j += 1
        group = visible[i:j]
        if len(group) >= 2 and (group[0].lstrip().startswith('|') or re.search(r'\|\s*:?-', group[1])):
            width = len(cells(group[0]))
            separator = cells(group[1])
            if len(separator) != width or not all(re.fullmatch(r':?-+:?', c) for c in separator):
                emit('REN-007', i + 2, 'ERROR', '表格缺少有效分隔行或分隔列数不符')
            for k, line in enumerate(group[2:], i + 3):
                if len(cells(line)) != width:
                    emit('REN-007', k, 'ERROR', '表格数据列数与表头不符')
        i = j

    # Heuristic density hints, only prose paragraphs; never a semantic verdict.
    short_run = 0
    for match in re.finditer(r'[^\n]+(?:\n(?!\n)[^\n]+)*', body):
        part = match.group()
        number = body.count('\n', 0, match.start()) + 1
        prose = not any(re.match(r'\s*(?:#|>|[-+*] |\d+[.)] |\|)', line) for line in part.splitlines())
        prose = prose and not re.fullmatch(r'\s*\*\*[^*]+\*\*\s*', part)
        short_run = short_run + 1 if prose and len(part) <= 35 else 0
        if short_run == 3:
            emit('PRE-001', number, 'WARNING', '连续三个短段；人工判断是否同一主题被切碎')
        if prose and len(part) > 800:
            emit('PRE-002', number, 'WARNING', '正文段超过 800 字符；人工检查文字墙')
    return sorted(findings, key=lambda d: (d['line'], d['rule_id']))


def signature(findings):
    return [{k: d[k] for k in ('rule_id', 'line', 'severity')} for d in findings]


def test_all():
    data = registry_check()
    known = {r['rule_id'] for r in data['rules']}
    expected = json.loads((ROOT / 'tests/expected/cases.json').read_text())
    covered = set()
    failures = 0
    for case in expected:
        file = ROOT / case['file']
        covered.add(case['file'])
        actual = signature(scan(file.read_text(encoding='utf-8')))
        ok = actual == case['diagnostics']
        if case.get('manual_review'):
            ok = ok and all(r in known for r in case['manual_review']) and bool(case.get('reason'))
        ok = ok and all(d['rule_id'] in known for d in actual)
        if '/invalid/' in case['file']:
            ok = ok and bool(actual or case.get('manual_review'))
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'} {case['file']}" + (' (人工判定样本；仅核对检测结果与记录)' if case.get('manual_review') else ''))
        if not ok:
            print(f'  expected={case["diagnostics"]}\n  actual={actual}')
    fixtures = {str(f.relative_to(ROOT)) for f in (ROOT / 'tests/fixtures').rglob('*.md')}
    if not fixtures <= covered:
        failures += 1
        print('FAIL 未登记 fixture', sorted(fixtures - covered))
    # Mutations independently exercise schema requirements and unique IDs.
    import copy
    mutations = []
    bad = copy.deepcopy(data); del bad['rules'][0]['title']; mutations.append(bad)
    bad = copy.deepcopy(data); bad['rules'][0]['status'] = 'proposed'; mutations.append(bad)
    bad = copy.deepcopy(data); bad['rules'][0]['exceptions'] = 'none'; mutations.append(bad)
    bad = copy.deepcopy(data); bad['rules'][0]['rule_id'] = 'REN-999'; mutations.append(bad)
    bad = copy.deepcopy(data); bad['rules'].append(dict(bad['rules'][0], title='重复编号')); mutations.append(bad)
    for idx, bad in enumerate(mutations, 1):
        try:
            registry_check(bad)
        except ValueError:
            print(f'PASS schema mutation {idx}')
        else:
            failures += 1
            print(f'FAIL schema mutation {idx}')
    for version in ['0.2.1', '1.0.0', '2.1.0-rc.1+build.7']:
        future = copy.deepcopy(data)
        future['standard_version'] = version
        registry_check(future)
        print(f'PASS independent standard version {version}')
    for key, value in [('standard_version', '01.2.0'), ('standard_version', '1.0.0-01'), ('schema_version', 2)]:
        bad = copy.deepcopy(data)
        bad[key] = value
        try:
            registry_check(bad)
        except ValueError:
            print(f'PASS reject {key}={value}')
        else:
            failures += 1
            print(f'FAIL accepted {key}={value}')
    # Test both directions of example links, not only file existence.
    bad = copy.deepcopy(data)
    bad['rules'][0]['examples']['good'] = ['examples/good/compact.md']
    try:
        registry_check(bad)
    except ValueError:
        print('PASS reject incorrect example mapping')
    else:
        failures += 1
        print('FAIL accepted incorrect example mapping')
    standard = (ROOT / 'STANDARD.md').read_text()
    mentioned = set(re.findall(r'`((?:SEM|PRE|REN)-[0-9]{3})`', standard))
    sync = mentioned == known and data['standard_version'] in standard
    failures += not sync
    print(('PASS' if sync else 'FAIL') + ' canonical rule references/version (not semantic proof)')
    # Coverage anchors prevent accidental omission; explanation quality remains human-reviewed.
    coverage = json.loads((ROOT / 'tests/expected/policy-coverage.json').read_text())
    for topic, anchors in coverage.items():
        ok = all(anchor in standard for anchor in anchors)
        failures += not ok
        print(('PASS' if ok else 'FAIL') + ' policy coverage: ' + topic)
    public_files = [ROOT / name for name in ['README.md', 'STANDARD.md', 'CHANGELOG.md', 'references/README.md']]
    public_files += list((ROOT / 'examples/good').glob('*.md'))
    clean_docs = all(not scan(file.read_text()) for file in public_files)
    failures += not clean_docs
    print(('PASS' if clean_docs else 'FAIL') + ' maintained docs and good examples strict gate')
    if not clean_docs:
        for file in public_files:
            for finding in scan(file.read_text()):
                print(file.relative_to(ROOT), finding)
    # No private snapshots are required by tests. Scan distributable text without Git or local sources.
    private_prefix = '/' + 'mnt' + '/'
    absolute = re.compile(re.escape(private_prefix) + r'[a-z]/|\b[A-Za-z]:[\\/]|/' + 'home' + r'/[^/\s]+/')
    leaks = []
    for folder in ['sources']:
        if (ROOT / folder).exists():
            leaks.append(folder)
    for file in ROOT.rglob('*'):
        relative = file.relative_to(ROOT)
        if any(part in {'.git', '.local-sources', '.venv', '__pycache__'} for part in relative.parts) or not file.is_file():
            continue
        if file.suffix in {'.md', '.yaml', '.yml', '.json', '.py', '.txt'} and absolute.search(file.read_text()):
            leaks.append(relative.as_posix())
    failures += bool(leaks)
    print(('FAIL ' + ', '.join(leaks) if leaks else 'PASS') + ' public working-tree path/source audit (not history cleanup)')
    print(f'{"FAIL" if failures else "PASS"}: {len(expected)} fixtures; schema/version/mapping, coverage and public checks; {failures} failures')
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', type=Path)
    parser.add_argument('--schema', action='store_true')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--strict', action='store_true', help='WARNING 也返回非零')
    args = parser.parse_args()
    try:
        if args.test:
            return test_all()
        if args.schema:
            data = registry_check()
            print(f'PASS schema + unique rule_id: {len(data["rules"])} rules')
        findings = []
        for path in args.paths:
            if not path.is_file():
                raise ValueError(f'文件不存在: {path}')
            findings.extend(dict(file=str(path), **d) for d in scan(path.read_text(encoding='utf-8')))
        if args.json:
            print(json.dumps(findings, ensure_ascii=False, indent=2))
        else:
            for d in findings:
                print(f'{d["severity"]} {d["file"]}:{d["line"]} {d["rule_id"]} {d["message"]}')
            if args.paths:
                print('INFO 人工检查：语义选择、真实从属、标题价值、流程方向；静态通过不代表全文合规。')
                print(f'ERROR={sum(d["severity"] == "ERROR" for d in findings)} WARNING={sum(d["severity"] == "WARNING" for d in findings)}')
        if not (args.schema or args.test or args.paths):
            parser.error('请提供文件，或使用 --schema / --test')
        return int(any(d['severity'] == 'ERROR' or args.strict for d in findings))
    except (ValueError, OSError) as exc:
        print(f'ERROR {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
