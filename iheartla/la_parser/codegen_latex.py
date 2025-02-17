from .codegen import *
from .type_walker import *


class CodeGenLatex(CodeGen):
    def __init__(self, parse_type=ParserTypeEnum.LATEX):
        super().__init__(parse_type)

    def init_type(self, type_walker, func_name):
        super().init_type(type_walker, func_name)
        self.local_func_parsing = False
        self.uni_convert_dict = {'ᵢ': '\\textsubscript{i}', 'ⱼ': '\\textsubscript{j}', 'ᵣ': '\\textsubscript{r}',
                                 'ᵤ': '\\textsubscript{u}', 'ᵥ': '\\textsubscript{v}', '𝟙': '\\mathbb{ 1 }',
                                 '𝐚': '\\textbf{a}', '𝐛': '\\textbf{b}', '𝐜': '\\textbf{c}', '𝐝': '\\textbf{d}', '𝐞': '\\textbf{e}',
                                 '𝐟': '\\textbf{f}', '𝐠': '\\textbf{g}', '𝐡': '\\textbf{h}', '𝐢': '\\textbf{i}', '𝐣': '\\textbf{j}',
                                 '𝐤': '\\textbf{k}', '𝐥': '\\textbf{l}', '𝐦': '\\textbf{m}', '𝐧': '\\textbf{n}', '𝐨': '\\textbf{o}',
                                 '𝐩': '\\textbf{p}', '𝐪': '\\textbf{q}', '𝐫': '\\textbf{r}', '𝐬': '\\textbf{s}', '𝐭': '\\textbf{t}',
                                 '𝐮': '\\textbf{u}', '𝐯': '\\textbf{v}', '𝐰': '\\textbf{w}', '𝐱': '\\textbf{x}', '𝐲': '\\textbf{y}',
                                 '𝐳': '\\textbf{z}', '⩽': '\\leq', '⩾': '\\geq'}
        self.pre_str = r'''
\documentclass[12pt]{article}
\usepackage{mathdots}
\usepackage[bb=boondox]{mathalfa}
\usepackage{mathtools}
\usepackage{amssymb}
'''[1:]
        self.pre_str += r'''
\usepackage{libertine}
'''[1:]
        self.pre_str += r'''
\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator*{\argmin}{arg\,min}
\usepackage[paperheight=8in,paperwidth=4in,margin=.3in,heightrounded]{geometry}
\let\originalleft\left
\let\originalright\right
\renewcommand{\left}{\mathopen{}\mathclose\bgroup\originalleft}
\renewcommand{\right}{\aftergroup\egroup\originalright}
\begin{document}

\begin{center}
\resizebox{\textwidth}{!} 
{
\begin{minipage}[c]{\textwidth}
\begin{align*}
'''[1:]
        self.post_str = r'''
\end{align*}
\end{minipage}
}
\end{center}

\end{document}
'''[1:]

    def convert_special_marks(self, name):
        for mark in ['̃', '̂', '̄']:
            if mark in name:
                return "\\textit{{{}}}".format(name)
        return "\\mathit{{{}}}".format(name)

    def convert_special_syms(self, param):
        special_list = ['_', '&', '^', '%', '$', '#', '{', '}']
        text = param.replace('\\', '\\textbackslash{}')
        for special in special_list:
            text = text.replace(special, '\\{}'.format(special))
        return text

    def convert_unicode(self, name):
        if '`' not in name:
            return self.convert_special_marks(name)
            # return name
        if '`$' not in name and '$`' not in name:
            name = "`${}$`".format(name[1:-1])
        text = name.replace('`', '')
        pattern = re.compile("\$(?P<context>.*)\$")
        res = ''
        first = True
        end = 0
        for m in pattern.finditer(name):
            if first:
                tmp = self.convert_special_syms(text[0:m.start()-1])
                if len(tmp) > 0:
                    res += "\\textit{{{}}}".format(tmp)
                first = False
            end = m.end()
            res += m.group('context')
        tmp = self.convert_special_syms(text[end-1:])
        if len(tmp) > 0:
            res += "\\textit{{{}}}".format(tmp)
        return res

    def visit_id(self, node, **kwargs):
        if node.contain_subscript():
            subs_list = []
            for subs in node.subs:
                subs_list.append(self.convert_unicode(subs))
            content = self.convert_unicode(node.main_id) + '_{' + ','.join(subs_list) + '}'
        else:
            content = self.convert_unicode(node.get_name())
        return content

    def visit_MatrixVdots(self, node, **kwargs):
        return "\\vdots"

    def visit_MatrixCdots(self, node, **kwargs):
        return "\\cdots"

    def visit_MatrixIddots(self, node, **kwargs):
        return "\\iddots"

    def visit_MatrixDdots(self, node, **kwargs):
        return "\\ddots"

    def visit_constant(self, node, **kwargs):
        content = ''
        if node.c_type == ConstantType.ConstantPi:
            content = '\\pi'
        elif node.c_type == ConstantType.ConstantE:
            content = 'e'
        return content

    def visit_double(self, node, **kwargs):
        return str(node.value)

    def visit_fraction(self, node, **kwargs):
        return str(node.unicode)

    def visit_integer(self, node, **kwargs):
        return str(node.value)

    def visit_IdentifierSubscript(self, node, **kwargs):
        right = []
        for value in node.right:
            right.append(self.visit(value, **kwargs))
        return self.visit(node.left, **kwargs) + '_{' + ','.join(right) + '}'

    def visit_IdentifierAlone(self, node, **kwargs):
        if node.value:
            value = node.value
        else:
            special_list = ['_', '&', '^', '%', '$', '#', '{', '}']
            text = node.id
            text = text.replace('\\', '\\textbackslash{}')
            for special in special_list:
                text = text.replace(special, '\\{}'.format(special))
            value = self.convert_special_marks(text)
        return value

    def visit_import(self, node, **kwargs):
        if node.package:
            content = "\\text{{from {} import {}}}\\\\\n".format(node.package.get_name(), ", ".join(node.get_name_list()))
        else:
            if len(node.params) > 0:
                params_str = ''
                for index in range(len(node.params)):
                    params_str += self.visit(node.params[index], **kwargs)
                    if index < len(node.params) - 1:
                        params_str += node.separators[index] + ''
                params_str = params_str.replace('\\mathit{', '\\textit{')
                content = "\\text{{from {}({}) import {}}}\\\\\n".format(node.module.get_name(), params_str, ", ".join(node.get_name_list()))
            else:
                content = "\\text{{from {}() import {}}}\\\\\n".format(node.module.get_name(), ", ".join(node.get_name_list()))
        return content

    def visit_start(self, node, **kwargs):
        content = ""
        # for directive in node.directives:
        #     content += self.visit(directive, **kwargs)
        pre_param = False
        pre_exp = False
        # pre_align = "\\begin{center}\n\\resizebox{\\linewidth}{!}{\n\\begin{minipage}[c]{\\linewidth}\n"
        # post_align = "\\end{minipage}\n}\n\\end{center}\n"
        pre_align = ""
        post_align = ""
        for vblock in node.vblock:
            if vblock.node_type != IRNodeType.ParamsBlock:
                if pre_param or (not pre_param and not pre_exp):
                    content += pre_align
                    # content += "\\begin{align*}\n"
                # elif pre_exp:
                #     content += " \\\\\n"
                block_content = self.visit(vblock, **kwargs)
                if vblock.node_type != IRNodeType.Assignment and vblock.node_type != IRNodeType.LocalFunc:
                    # single expression
                    block_content = " \\omit \\span " + block_content
                content += block_content + " \\\\\n"
            else:
                # params
                if not (not pre_param and not pre_exp) and not vblock.annotation:
                    # params block without 'where'
                    content += "\\\\\n"
                if pre_exp:
                    # content += "\n\\end{align*}\n"
                    content += post_align
                content += self.visit(vblock, **kwargs)
            pre_param = vblock.node_type == IRNodeType.ParamsBlock
            pre_exp = vblock.node_type != IRNodeType.ParamsBlock
        if pre_exp:
            # content += "\n\\end{align*}\n"
            content += post_align
        # handle unicode special characters
        for key, value in self.uni_convert_dict.items():
            if key in content:
                content = content.replace(key, value)
        self.code_frame.main = self.pre_str + content + self.post_str
        return content

    def visit_block(self, node, **kwargs):
        ret = []
        for stmt in node.stmts:
            ret.append(self.visit(stmt, **kwargs))
        return '\\\\'.join(ret)

    def visit_params_block(self, node, **kwargs):
        content = self.visit(node.conds, **kwargs)
        # content = "\\begin{itemize}\n" + self.visit(node.conds, **kwargs) + '\\end{itemize}\n\n'
        if node.annotation:
            content = "\\intertext{{{}}} ".format(node.annotation) + "\n" + content
        content += "\\\\\n"
        return content

    def visit_where_conditions(self, node, **kwargs):
        ret = []
        for val in node.value:
            ret.append(self.visit(val, **kwargs) + " \\\\\n")
        return ''.join(ret)

    def visit_where_condition(self, node, **kwargs):
        id_list = [self.visit(id0, **kwargs) for id0 in node.id]
        type_content = self.visit(node.type, **kwargs)
        if self.local_func_parsing:
            content = "{} \\in {}".format(','.join(id_list), type_content)
        else:
            content = "{} & \\in {}".format(','.join(id_list), type_content)
        if node.desc:
            content += " \\text{{ {}}}".format(self.convert_special_syms(node.desc))
        return content

    def visit_matrix_type(self, node, **kwargs):
        id1 = self.visit(node.id1, **kwargs)
        id2 = self.visit(node.id2, **kwargs)
        type_str = '\\mathbb{R}'
        if node.type == 'ℤ':
            type_str = '\\mathbb{Z}'
        content = "{}^{{ {} \\times {} }}".format(type_str, id1, id2)
        if node.la_type.sparse:
            content += " ,\\text{ sparse}"
        if node.la_type.index_type:
            content += " ,\\text{ index}"
        return content

    def visit_vector_type(self, node, **kwargs):
        id1 = self.visit(node.id1, **kwargs)
        type_str = '\\mathbb{R}'
        if node.type == 'ℤ':
            type_str = '\\mathbb{Z}'
        content = "{}^{{ {}}}".format(type_str, id1)
        if node.la_type.index_type:
            content += " ,\\text{ index}"
        return content

    def visit_scalar_type(self, node, **kwargs):
        content = "\\mathbb{R}"
        if node.is_int:
            content = "\\mathbb{Z}"
        if node.la_type.index_type:
            content += " ,\\text{ index}"
        return content

    def visit_set_type(self, node, **kwargs):
        content = ''
        int_list = []
        cnt = 1
        if node.type:
            for t in node.type:
                if t == 'ℤ':
                    int_list.append('\\mathbb{Z}')
                else:
                    int_list.append('\\mathbb{R}')
            content += " \\times ".join(int_list)
        elif node.type1:
            cnt = node.cnt
            if node.type1 == 'ℤ':
                content += '\\mathbb{{Z}}^{{ {} }}'.format(cnt)
            else:
                content += '\\mathbb{{R}}^{{ {} }}'.format(cnt)
        elif node.type2:
            cnt = node.cnt
            if node.type2 == 'ℤ':
                content += '\\mathbb{{Z}}^{{ {} }}'.format(cnt)
            else:
                content += '\\mathbb{{R}}^{{ {} }}'.format(cnt)
        content = '\\{' + content + '\\}'
        if node.la_type.index_type:
            content += " ,\\text{ index}"
        return content

    def visit_function_type(self, node, **kwargs):
        ret = self.visit(node.ret, **kwargs)
        if len(node.params) == 0:
            if node.empty:
                params_str = '\\varnothing'
            else:
                params_str = '\{\}'
        else:
            params_str = ''
            for index in range(len(node.params)):
                params_str += self.visit(node.params[index], **kwargs)
                if index < len(node.params)-1:
                    params_str += node.separators[index] + ''
        return params_str + '\\rightarrow ' + ret

    def visit_assignment(self, node, **kwargs):
        content = ''
        lhs_list = []
        for cur_index in range(len(node.left)):
            lhs_list.append(self.visit(node.left[cur_index], **kwargs))
        if node.right[0].node_type == IRNodeType.Optimize:
            content = self.visit(node.right[0], **kwargs)
        else:
            rhs_list = []
            for cur_index in range(len(node.right)):
                rhs_list.append(self.visit(node.right[cur_index], **kwargs))
            content = ','.join(lhs_list) + " & = " + ','.join(rhs_list)
        self.code_frame.expr += content +'\n'
        self.code_frame.expr_dict[node.raw_text] = content
        return content

    def visit_expression(self, node, **kwargs):
        value = self.visit(node.value, **kwargs)
        if node.sign:
            value = node.sign + value
        return value

    def visit_add(self, node, **kwargs):
        return self.visit(node.left, **kwargs) + " + " + self.visit(node.right, **kwargs)

    def visit_sub(self, node, **kwargs):
        return self.visit(node.left, **kwargs) + " - " + self.visit(node.right, **kwargs)

    def visit_add_sub(self, node, **kwargs):
        return self.visit(node.left, **kwargs) + " {} ".format(node.op) + self.visit(node.right, **kwargs)

    def visit_mul(self, node, **kwargs):
        if node.op == MulOpType.MulOpDot:
            return self.visit(node.left, **kwargs) + " \\cdot " + self.visit(node.right, **kwargs)
        else:
            return self.visit(node.left, **kwargs) + self.visit(node.right, **kwargs)

    def visit_div(self, node, **kwargs):
        if node.op == DivOpType.DivOpSlash:
            left_content = self.visit(node.left, **kwargs)
            right_content = self.visit(node.right, **kwargs)    
            return "\\frac{" + left_content + "}{" +right_content + "}"
        else:
            return self.visit(node.left, **kwargs) + "÷" + self.visit(node.right, **kwargs)

    def visit_summation(self, node, **kwargs):
        if node.cond:
            sub = '{' + self.visit(node.cond, **kwargs) + '}'
        else:
            if node.enum_list:
                kwargs['is_sub'] = True
                sub = ','.join(node.enum_list)
                del kwargs['is_sub']
                range = self.visit(node.range, **kwargs)
                sub += "\in " + range
            else:
                kwargs['is_sub'] = True
                sub = self.visit(node.id, **kwargs)
                del kwargs['is_sub']
        return "\\sum_{" + sub + "} " + self.visit(node.exp, **kwargs)

    def visit_function(self, node, **kwargs):
        params = []
        if node.params:
            for param in node.params:
                params.append(self.visit(param, **kwargs))
        params_str = ''
        if len(node.params) > 0:
            for index in range(len(node.params)):
                params_str += self.visit(node.params[index], **kwargs)
                if index < len(node.params)-1:
                    params_str += node.separators[index] + ''
        return self.visit(node.name, **kwargs) + '\\left( ' + params_str + ' \\right)'

    def visit_local_func(self, node, **kwargs):
        params_str = ''
        if len(node.params) > 0:
            for index in range(len(node.params)):
                params_str += self.visit(node.params[index], **kwargs)
                if index < len(node.params)-1:
                    params_str += node.separators[index] + ''
        if node.def_type == LocalFuncDefType.LocalFuncDefParenthesis:
            def_params = '\\left( ' + params_str + ' \\right)'
        else:
            def_params = '\\left[ ' + params_str + ' \\right]'
        expr_list = []
        for cur_index in range(len(node.expr)):
            expr_list.append(self.visit(node.expr[cur_index], **kwargs))
        content = self.visit(node.name, **kwargs) + def_params + " & = " + ', '.join(expr_list)
        self.code_frame.expr += content + '\n'
        self.code_frame.expr_dict[node.raw_text] = content
        if len(node.defs) > 0:
            self.local_func_parsing = True
            par_list = []
            for par in node.defs:
                par_list.append(self.visit(par, **kwargs))
            # content += "\\intertext{{{}}} ".format('where') + ', '.join(par_list)
            content += ' \\text{{ where }}  ' + ', '.join(par_list)
            self.local_func_parsing = False
        return content

    def visit_if(self, node, **kwargs):
        ret_info = self.visit(node.cond, **kwargs)
        # ret_info = "if " + ret_info + ":\n"
        return ret_info

    def visit_condition(self, node, **kwargs):
        if len(node.cond_list) > 1:
            content_list = []
            for condition in node.cond_list:
                info = self.visit(condition)
                content_list.append(info)
            if node.cond_type == ConditionType.ConditionAnd:
                content = ' \\text{{ and }}'.join(content_list)
            else:
                content = ' \\text{{ or }}'.join(content_list)
            return content
        if node.tex_node:
            return self.visit(node.tex_node, **kwargs)
        return self.visit(node.cond_list[0])

    def visit_in(self, node, **kwargs):
        item_list = []
        for item in node.items:
            item_info = self.visit(item, **kwargs)
            item_list.append(item_info)
        right_info = self.visit(node.set, **kwargs)
        if len(item_list) > 1:
            return '\\left( {} \\right) \\in {} '.format(', '.join(item_list), right_info)
        else:
            return '{} \\in {} '.format(', '.join(item_list), right_info)

    def visit_not_in(self, node, **kwargs):
        item_list = []
        for item in node.items:
            item_info = self.visit(item, **kwargs)
            item_list.append(item_info)
        right_info = self.visit(node.set, **kwargs)
        if len(item_list) > 1:
            return '\\left( {} \\right) \\notin {} '.format(', '.join(item_list), right_info)
        else:
            return '{} \\notin {} '.format(', '.join(item_list), right_info)

    def visit_bin_comp(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        return left_info + ' {} '.format(node.op) + right_info

    def visit_sub_expr(self, node, **kwargs):
        return '\\left( ' + self.visit(node.value, **kwargs) + ' \\right)'

    def visit_cast(self, node, **kwargs):
        return self.visit(node.value, **kwargs)

    def visit_multi_conditionals(self, node, **kwargs):
        ifs = self.visit(node.ifs, **kwargs)
        if node.other:
            other = self.visit(node.other, **kwargs)
            content = '{} {} {} & \\text{{otherwise}} {}'.format("\\begin{cases}", ifs, other, "\\end{cases}")
        else:
            content = '{} {} {} '.format("\\begin{cases}", ifs, "\\end{cases}")
        return content

    def visit_sparse_matrix(self, node, **kwargs):
        if node.id1:
            id1_info = self.visit(node.id1, **kwargs)
            id2_info = self.visit(node.id2, **kwargs)
        ifs = self.visit(node.ifs, **kwargs)
        if node.other:
            other = self.visit(node.other, **kwargs)
            content = '{} {} {} & \\text{{otherwise}} {}'.format("\\begin{cases}", ifs, other, "\\end{cases}")
        else:
            content = '{} {} {} '.format("\\begin{cases}", ifs, "\\end{cases}")
        return content

    def visit_sparse_ifs(self, node, **kwargs):
        content = ''
        for cond in node.cond_list:
            content += (self.visit(cond, **kwargs) + " \\\\")
        return content

    def visit_sparse_if(self, node, **kwargs):
        stat_info = self.visit(node.stat, **kwargs)
        cond_info = self.visit(node.cond, **kwargs)
        return '{} & \\text{{if }}  {}'.format(stat_info, cond_info)

    def visit_sparse_other(self, node, **kwargs):
        content = ''
        return CodeNodeInfo('    '.join(content))

    def visit_num_matrix(self, node, **kwargs):
        kwargs['is_sub'] = True
        id1_info = self.visit(node.id1, **kwargs)
        if node.id:
            content = "I_{{ {} }}".format(id1_info)
        else:
            content = "\\mathbb{{ {} }}".format(node.left)
            if node.id2:
                id2_info = self.visit(node.id2, **kwargs)
                content = "{}_{{ {},{} }}".format(content, id1_info, id2_info)
            else:
                content = "{}_{{ {} }}".format(content, id1_info)
        return content

    def visit_matrix_index(self, node, **kwargs):
        main_info = self.visit(node.main, **kwargs)
        kwargs['is_sub'] = True
        if node.row_index is not None:
            row_info = self.visit(node.row_index, **kwargs)
        else:
            row_info = '*'
        if node.col_index is not None:
            col_info = self.visit(node.col_index, **kwargs)
        else:
            col_info = '*'
        return "{}_{{{}, {}}}".format(main_info, row_info, col_info)

    def visit_vector_index(self, node, **kwargs):
        main_info = self.visit(node.main, **kwargs)
        kwargs['is_sub'] = True
        index_info = self.visit(node.row_index, **kwargs)
        return "{}_{{ {} }}".format(main_info, index_info)

    def visit_sequence_index(self, node, **kwargs):
        main_info = self.visit(node.main, **kwargs)
        kwargs['is_sub'] = True
        main_index_info = self.visit(node.main_index, **kwargs)
        if node.slice_matrix:
            if node.row_index is not None:
                row_info = self.visit(node.row_index, **kwargs)
                content = "{}_{{ {}, {}, *}}".format(main_info, main_index_info, row_info)
            else:
                col_info = self.visit(node.col_index, **kwargs)
                content = "{}_{{ {}, *, {}}}".format(main_info, main_index_info, col_info)
        else:
            if node.row_index is not None:
                row_info = self.visit(node.row_index, **kwargs)
                if node.col_index is not None:
                    col_info = self.visit(node.col_index, **kwargs)
                    content = "{}_{{ {}, {}, {}}}".format(main_info, main_index_info, row_info, col_info)
                else:
                    content = "{}_{{ {}, {} }}".format(main_info, main_index_info, row_info)
            else:
                content = "{}_{{ {} }}".format(main_info, main_index_info)
        return content

    def visit_seq_dim_index(self, node, **kwargs):
        main_info = self.visit(node.main, **kwargs)
        kwargs['is_sub'] = True
        main_index_info = self.visit(node.main_index, **kwargs)
        content = "{}_{{ {} }}".format(main_info, main_index_info)
        return content

    def visit_matrix(self, node, **kwargs):
        return '\\begin{bmatrix}\n' + self.visit(node.value, **kwargs) + '\\end{bmatrix}'

    def visit_vector(self, node, **kwargs):
        content_list = []
        for item in node.items:
            content_list.append(self.visit(item, **kwargs))
        return '\\begin{pmatrix}\n' + '\\\\'.join(content_list) + '\\end{pmatrix}'

    def visit_MatrixRows(self, node, **kwargs):
        ret = []
        for val in node.value:
            ret.append(self.visit(val, **kwargs))
        return ''.join(ret)

    def visit_matrix_rows(self, node, **kwargs):
        ret = []
        if node.rs:
            ret.append(self.visit(node.rs, **kwargs))
        if node.r:
            ret.append(self.visit(node.r, **kwargs))
        return ''.join(ret)

    def visit_matrix_row(self, node, **kwargs):
        ret = []
        if node.rc:
            ret.append(self.visit(node.rc, **kwargs))
        if node.exp:
            ret.append(self.visit(node.exp, **kwargs))
        return ' & '.join(ret) + "\\\\\n"

    def visit_matrix_row_commas(self, node, **kwargs):
        ret = []
        if node.value:
            ret.append(self.visit(node.value, **kwargs))
        if node.exp:
            ret.append(self.visit(node.exp, **kwargs))
        return ' & '.join(ret)

    def visit_exp_in_matrix(self, node, **kwargs):
        value = self.visit(node.value, **kwargs)
        if node.sign:
            value = node.sign + value
        return value

    def visit_power(self, node, **kwargs):
        base_info = self.visit(node.base, **kwargs)
        if node.t:
            base_info = "{{{}}}^T".format(base_info)
        elif node.r:
            base_info = base_info + "^{-1}"
        else:
            if node.power.node_type == IRNodeType.Factor and node.power.sub:  # sub expression
                power_info = self.visit(node.power.sub.value, **kwargs)
            else:
                power_info = self.visit(node.power, **kwargs)
            if node.base.node_type == IRNodeType.Norm:
                # don't enclose norms in {} this causes ugly space.
                base_info = "{}^{{{}}}".format(base_info, power_info)
            else:
                base_info = "{{{}}}^{{{}}}".format(base_info, power_info)
        return base_info

    def visit_solver(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        if node.pow:
            return left_info + '^{-1}' + right_info
        return left_info + ' \setminus ' + right_info

    def visit_norm(self, node, **kwargs):
        if node.value.la_type.is_scalar():
            content = "\\left|{}\\right|".format(self.visit(node.value, **kwargs))
        else:
            value_content = self.visit(node.value, **kwargs)
            content = "\\left\\|{}\\right\\|".format(value_content)
            if node.value.la_type.is_vector():
                if node.norm_type == NormType.NormDet:
                    content = "\\left|{}\\right|".format(value_content)
                elif node.norm_type == NormType.NormInteger:
                    if node.sub is not None:
                        content += "_{}".format(node.sub)
                elif node.norm_type == NormType.NormMax:
                    content += "_\\infty"
                elif node.norm_type == NormType.NormIdentifier:
                    sub_info = self.visit(node.sub, **kwargs)
                    content += "_{{{}}}".format(sub_info)
            elif node.value.la_type.is_matrix():
                if node.norm_type == NormType.NormDet:
                    content = "\\left|{}\\right|".format(value_content)
                elif node.norm_type == NormType.NormFrobenius:
                    if node.sub is not None:
                        content += "_F"
                elif node.norm_type == NormType.NormNuclear:
                    content += "_*"
        return content

    def visit_transpose(self, node, **kwargs):
        return "{{{}}}^T".format(self.visit(node.f, **kwargs))

    def visit_pseudoinverse(self, node, **kwargs):
        return "{{{}}}^+".format(self.visit(node.f, **kwargs))

    def visit_squareroot(self, node, **kwargs):
        if node.value.node_type == IRNodeType.Factor and node.value.sub:  # sub expression
            content = self.visit(node.value.sub.value, **kwargs)
        else:
            content = self.visit(node.value, **kwargs)
        return "\sqrt{{{}}}".format(content)

    def visit_derivative(self, node, **kwargs):
        return "\\partial" + self.visit(node.value, **kwargs)

    def visit_optimize(self, node, **kwargs):
        assign_node = node.get_ancestor(IRNodeType.Assignment)
        category = ''
        if node.opt_type == OptimizeType.OptimizeMin:
            category = '\\min'
        elif node.opt_type == OptimizeType.OptimizeMax:
            category = '\\max'
        elif node.opt_type == OptimizeType.OptimizeArgmin:
            category = '\\argmin'
        elif node.opt_type == OptimizeType.OptimizeArgmax:
            category = '\\argmax'
        content = "\\begin{aligned} "
        if assign_node:
            self.visiting_lhs = True
            lhs_list = []
            for cur_index in range(len(assign_node.left)):
                lhs_list.append(self.visit(assign_node.left[cur_index], **kwargs))
            content += "{} = ".format(', '.join(lhs_list))
            self.visiting_lhs = False
        kwargs['is_sub'] = True
        param_list = []
        for par in node.def_list:
            param_list.append(self.visit(par, **kwargs))
        del kwargs['is_sub']
        content += "{}_{{{}}} \\quad & {} \\\\\n".format(category, ", ".join(param_list).replace('&', ''), self.visit(node.exp, **kwargs))
        if len(node.cond_list) > 0:
            content += "\\textrm{s.t.} \\quad &"
            constraint_list = []
            for cond_node in node.cond_list:
                constraint_list.append("{}".format(self.visit(cond_node, **kwargs)))
            content += "\\\\\n & ".join(constraint_list)
            content += "\n"
        content += "\\end{aligned}"
        if not assign_node:
            self.code_frame.expr += content +'\n'
            self.code_frame.expr_dict[node.raw_text] = content
        return content

    def visit_domain(self, node, **kwargs):
        return ""

    def visit_integral(self, node, **kwargs):
        lower = self.visit(node.domain.lower, **kwargs)
        upper = self.visit(node.domain.upper, **kwargs)
        exp = self.visit(node.exp, **kwargs)
        base = self.visit(node.base, **kwargs)
        return "\\int_{{{}}}^{{{}}} {} d{}".format(lower, upper, exp, base)

    def visit_inner_product(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        content = "\\langle {} , {}\\rangle".format(left_info, right_info)
        if node.sub:
            content = "{{{}}}_{}".format(content, self.visit(node.sub, **kwargs))
        return content

    def visit_fro_product(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        return "{} : {}".format(left_info, right_info)

    def visit_hadamard_product(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        return "{} \\circ {}".format(left_info, right_info)

    def visit_cross_product(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        return "{} × {}".format(left_info, right_info)

    def visit_kronecker_product(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        return "{} \\otimes {}".format(left_info, right_info)

    def visit_dot_product(self, node, **kwargs):
        left_info = self.visit(node.left, **kwargs)
        right_info = self.visit(node.right, **kwargs)
        return "{} \\cdot {}".format(left_info, right_info)

    def visit_math_func(self, node, **kwargs):
        content = ''
        param_info = self.visit(node.param, **kwargs)
        if node.func_type == MathFuncType.MathFuncSin:
            content = 'sin'
        elif node.func_type == MathFuncType.MathFuncAsin:
            content = node.func_name  # 'asin'
        elif node.func_type == MathFuncType.MathFuncCos:
            content = 'cos'
        elif node.func_type == MathFuncType.MathFuncAcos:
            content = node.func_name  # 'acos'
        elif node.func_type == MathFuncType.MathFuncTan:
            content = 'tan'
        elif node.func_type == MathFuncType.MathFuncAtan:
            content = node.func_name  # 'atan'
        elif node.func_type == MathFuncType.MathFuncSinh:
            content = 'sinh'
        elif node.func_type == MathFuncType.MathFuncAsinh:
            content = node.func_name  # 'asinh'
        elif node.func_type == MathFuncType.MathFuncCosh:
            content = 'cosh'
        elif node.func_type == MathFuncType.MathFuncAcosh:
            content = node.func_name  # 'acosh'
        elif node.func_type == MathFuncType.MathFuncTanh:
            content = 'tanh'
        elif node.func_type == MathFuncType.MathFuncAtanh:
            content = node.func_name  # 'atanh'
        elif node.func_type == MathFuncType.MathFuncCot:
            content = 'cot'
        elif node.func_type == MathFuncType.MathFuncSec:
            content = 'sec'
        elif node.func_type == MathFuncType.MathFuncCsc:
            content = 'csc'
        elif node.func_type == MathFuncType.MathFuncAtan2:
            content = 'atan2'
            param_info += node.separator + ' ' + self.visit(node.remain_params[0], **kwargs)
        elif node.func_type == MathFuncType.MathFuncExp:
            content = 'exp'
        elif node.func_type == MathFuncType.MathFuncLog:
            return " \log{{ {} }}".format(param_info)
        elif node.func_type == MathFuncType.MathFuncLog2:
            return " \log_2{{ {} }}".format(param_info)
        elif node.func_type == MathFuncType.MathFuncLog10:
            return " \log_{{10}}{{ {} }}".format(param_info)
        elif node.func_type == MathFuncType.MathFuncLn:
            return " \ln{{ {} }}".format(param_info)
        elif node.func_type == MathFuncType.MathFuncSqrt:
            content = 'sqrt'
        elif node.func_type == MathFuncType.MathFuncTrace:
            content = node.func_name
        elif node.func_type == MathFuncType.MathFuncDiag:
            content = ' \mathop{\\text{diag}}'
        elif node.func_type == MathFuncType.MathFuncVec:
            content = ' \mathop{\\text{vec}}'
        elif node.func_type == MathFuncType.MathFuncDet:
            content = ' \mathop{\\text{det}}'
        elif node.func_type == MathFuncType.MathFuncRank:
            content = ' \mathop{\\text{rank}}'
        elif node.func_type == MathFuncType.MathFuncNull:
            content = ' \mathop{\\text{null}}'
        elif node.func_type == MathFuncType.MathFuncOrth:
            content = ' \mathop{\\text{orth}}'
        elif node.func_type == MathFuncType.MathFuncInv:
            content = ' \mathop{\\text{inv}}'
        return "{}\\left( {} \\right)".format(content, param_info)

    def visit_maxlist(self, node, **kwargs):
        if node.rest:
            left_content = self.visit(node.left, **kwargs)
            rest_content = self.visit(node.rest, **kwargs)
            return "{}, {}".format(left_content, rest_content)
        else:
            left_content = self.visit(node.left, **kwargs)
            return "{}".format(left_content)

    def visit_max(self, node, **kwargs):
        left_content = self.visit(node.left, **kwargs)
        rest_content  = self.visit(node.rest, **kwargs)
        return "max({}, {})".format(left_content, rest_content)

    def visit_minlist(self, node, **kwargs):
        if node.rest:
            left_content = self.visit(node.left, **kwargs)
            rest_content = self.visit(node.rest, **kwargs)
            return "{}, {}".format(left_content, rest_content)
        else:
            left_content = self.visit(node.left, **kwargs)
            return "{}".format(left_content)

    def visit_min(self, node, **kwargs):
        left_content = self.visit(node.left, **kwargs)
        rest_content  = self.visit(node.rest, **kwargs)
        return "min({}, {})".format(left_content, rest_content)

    def visit_floor(self, node, **kwargs):
        exp_info = self.visit(node.exp, **kwargs)
        exp_info = "floor({})".format(exp_info)
        return exp_info
