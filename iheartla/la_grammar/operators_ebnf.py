OPERATORS = r"""
# operators
operations
    =
    | solver_operator
    | norm_operator
    | power_operator
    | inner_product_operator
   #| frobenius_product_operator
    | hadamard_product_operator
    | cross_product_operator
    | kronecker_product_operator
    | sum_operator
    | integral_operator
    | trans_operator
    | sqrt_operator
    | function_operator
    | builtin_operators
    | pseudoinverse_operator
    ;


addition::Add
    =
    left:expression {hspace} op:'+' {hspace} right:term
    ;


subtraction::Subtract
    =
    left:expression {hspace} op:'-' {hspace} right:term
    ;

add_sub_operator::AddSub
    =
    left:expression {hspace} op:('+-'|'±') {hspace} right:term
    ;


multiplication::Multiply
    =
    left:term {hspace} op:'⋅' {hspace} right:factor
    | left:term {hspace} right:factor
    ;


division::Divide
    =
    left:term {hspace} op:('/'|'÷') {hspace} right:factor
    ;


power_operator::Power
    = base:factor t:'^T'
    | base:factor r:('^(-1)' | '⁻¹')
    | base:factor '^' power:factor
    | base:factor power:sup_integer
    ;

solver_operator::Solver
    = left:factor {hspace} '\' {hspace} right:factor
    | left:factor {hspace} p:('^(-1)' | '⁻¹') {hspace} right:factor
    ;

sum_operator::Summation
    = SUM '_' sub:identifier_alone {hspace}+ exp:term
    | SUM '_' sub:identifier_alone &'(' {hspace} exp:term
    | SUM '_(' {hspace} id:identifier_alone {hspace} 'for' {hspace} cond:if_condition {hspace} ')' {hspace}+ exp:term
    | SUM '_(' {hspace} enum+:identifier_alone {{hspace} ',' {hspace} enum+:identifier_alone} {hspace} IN {hspace} range:(function_operator | identifier_alone) {hspace} ')' {hspace}+ exp:term
    ;

# optimize_operator::Optimize
#    = 
#    {'with' {hspace} 'initial' {hspace} init+:statement {{hspace} ';' {hspace} init+:statement} {hspace} '\n'}
#    (min:MIN|max:MAX|amin:ARGMIN|amax:ARGMAX) '_(' {hspace} defs+:where_condition_terse {{hspace} ',' {hspace} defs+:where_condition_terse} {hspace}
#    ')' {hspace} exp:expression 
#    {{{hspace} {separator} {hspace}} SUBJECT_TO {{hspace} {separator} {hspace}} cond:multi_cond}
#    ;

max_operator::Max
    =
    MAX '('  {hspace} left:expression rest:max_list {hspace} ')'
    ;

max_list::MaxList
    = {hspace} ','  {hspace} left:expression rest:max_list
    | {hspace} ','  {hspace} left:expression
    ;

min_operator::Min
    =
    MIN '('  {hspace} left:expression rest:min_list {hspace} ')'
    ;

min_list::MinList
    = {hspace} ','  {hspace} left:expression rest:min_list
    | {hspace} ','  {hspace} left:expression
    ;

floor_operator::Floor
    =
    FLOOR '('  {hspace} exp:expression {hspace} ')'
    | '⌊' {hspace} exp:expression {hspace} '⌋'
    ;

multi_cond::MultiCond
    = {hspace} m_cond:multi_cond separator_with_space cond:atom_condition {hspace}
    | {hspace} cond:atom_condition {hspace}
    ;

integral_operator::Integral
    = (INT|'∫') '_' (d:domain | (lower:sub_factor {hspace} '^' {hspace} upper:sub_factor )) {hspace} exp:expression {hspace} '∂' id:identifier_alone
    ;

domain::Domain
    = '[' {hspace} lower:expression {hspace} ',' {hspace} upper:expression ']'
    ;

norm_operator::Norm
    = (double:'||' {hspace} value:expression {hspace} '||'
    | double:'‖' {hspace} value:expression {hspace} '‖'
    | single:'|' {hspace} value:expression {hspace} '|')
    [
    ( ('_' sub:(integer|'*'|'∞'|identifier_alone) | sub:sub_integer) ['^' power:factor | power:sup_integer])
    | ( '_(' sub:(integer|'*'|'∞'|identifier) ')' ['^' power:factor | power:sup_integer])
    | ( ('^' power:factor | power:sup_integer) ['_' sub:(integer|'*'|'∞'|identifier_alone) | sub:sub_integer] )
    ]
    ;

inner_product_operator::InnerProduct
    = (('<' {hspace} left:expression {hspace} ',' {hspace}  right:expression {hspace} '>')
    | ('⟨' {hspace} left:expression {hspace} ',' {hspace}  right:expression {hspace} '⟩'))
    {'_' sub:identifier}
    ;

frobenius_product_operator::FroProduct
    = left:factor {hspace} ':' {hspace}  right:factor
    ;

hadamard_product_operator::HadamardProduct
    = left:factor {hspace} '∘' {hspace}  right:factor
    ;

cross_product_operator::CrossProduct
    = left:factor {hspace} '×' {hspace}  right:factor
    ;

kronecker_product_operator::KroneckerProduct
    = left:factor {hspace} '⊗' {hspace}  right:factor
    ;

trans_operator::Transpose
    = f:factor /ᵀ/
    ;

pseudoinverse_operator::PseudoInverse
    = f:factor /⁺/
    ;
    
sqrt_operator::Squareroot
    = /√/ f:factor;

function_operator::Function
    = name:func_id '(' {{hspace} params+:expression {{hspace} separators+:params_separator {hspace} params+:expression}} {hspace}')'
    ;

predefined_built_operators
    =
    | exp_func
    | log_func
    | ln_func
    | sqrt_func
    ;

exp_func::ExpFunc
    = EXP '(' {hspace} param:expression {hspace} ')'
    ;

log_func::LogFunc
    = ( (f:/log[\u2082]/ | s: /log[\u2081][\u2080]/) '(' {hspace} param:expression {hspace} ')')
    | ( LOG [f:'_2' | s:'_10'] '(' {hspace} param:expression {hspace} ')')
    ;

ln_func::LnFunc
    = LN '(' {hspace} param:expression {hspace} ')'
    ;

sqrt_func::SqrtFunc
    = SQRT '(' {hspace} param:expression {hspace} ')'
    ;
"""