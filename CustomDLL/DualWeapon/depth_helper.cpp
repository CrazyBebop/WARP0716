/*
 * Frozen character-envelope depth helper, 2025-07-16 x86.
 * Copyright (C) 2026 Louis T Steinhil; GPL-3.0-or-later.
 * Recovered instruction-for-instruction from the accepted helper.
 * __stdcall(actor, completed quad, draw packet, scope); ret 16.
 * Scope mode 1 captures up to five character planes; mode 2 applies the
 * same bounded foreground Z adjustment to custom weapon vertices.
 * No X/Y, palette, resource or garment changes; diagnostic callbacks stay
 * optional and are zero in production. This is audited x86, not a hex blob.
 */
extern "C" __declspec(dllexport, naked) int __stdcall DualWeaponDepth(void*, void*, void*, void*)
{
	__asm
	{
		mov edx, dword ptr [esp + 4]
		sub esp, 0x18
		push esi
		push edi
		test edx, edx
		je label_0541
		cmp dword ptr [esp + 0x28], 0
		je label_0541
		mov ecx, dword ptr [esp + 0x2c]
		test ecx, ecx
		je label_0541
		mov esi, dword ptr [esp + 0x30]
		test esi, esi
		je label_0541
		mov eax, dword ptr [esi]
		cmp eax, 1
		je label_0044
		cmp eax, 2
		jne label_0541
	label_0044:
		mov dword ptr [esi], 0
		cmp dword ptr [esi + 4], edx
		jne label_0523
		cmp dword ptr [esi + 8], ecx
		jne label_0523
		mov ecx, dword ptr [esi + 0x10]
		test ecx, ecx
		je label_0523
		cmp eax, 1
		jne label_0370
		mov edi, dword ptr [esi + 0xc]
		cmp edi, 5
		jae label_0345
		mov esi, dword ptr [edx + 0x3c]
		mov eax, edx
		shr eax, 4
		movzx eax, al
		imul eax, eax, 0x88
		mov dword ptr [esp + 0x24], esi
		mov esi, dword ptr [esp + 0x30]
		add ecx, eax
		mov eax, dword ptr [edx + 0x38]
		test edi, edi
		je label_00b4
		cmp dword ptr [ecx], edx
		jne label_00b4
		cmp dword ptr [ecx + 4], eax
		jne label_00b4
		mov esi, dword ptr [esp + 0x24]
		cmp dword ptr [ecx + 8], esi
		mov esi, dword ptr [esp + 0x30]
		je label_00ed
	label_00b4:
		mov dword ptr [ecx + 4], eax
		mov eax, dword ptr [esp + 0x24]
		mov dword ptr [ecx], edx
		mov dword ptr [ecx + 8], eax
		mov dword ptr [ecx + 0xc], 0
		mov dword ptr [ecx + 0x24], 0
		mov dword ptr [ecx + 0x3c], 0
		mov dword ptr [ecx + 0x54], 0
		mov dword ptr [ecx + 0x6c], 0
		mov dword ptr [ecx + 0x84], 0
	label_00ed:
		lea edx, [edi + edi*2]
		mov dword ptr [ecx + edx*8 + 0x24], 0
		mov eax, dword ptr [ecx + 0xc]
		btr eax, edi
		mov dword ptr [ecx + 0xc], eax
		mov eax, dword ptr [esp + 0x28]
		movss xmm1, dword ptr [eax + 0x20]
		subss xmm1, dword ptr [eax]
		movss xmm2, dword ptr [eax + 4]
		movss xmm7, dword ptr [eax + 0x40]
		movss xmm5, dword ptr [eax + 0x44]
		subss xmm7, dword ptr [eax]
		movss xmm4, dword ptr [eax + 8]
		subss xmm5, xmm2
		movss xmm3, dword ptr [eax + 0x48]
		movss dword ptr [esp + 0x24], xmm1
		subss xmm3, xmm4
		movss xmm1, dword ptr [eax + 0x24]
		subss xmm1, xmm2
		movaps xmm0, xmm7
		movaps xmm6, xmm5
		mulss xmm6, dword ptr [esp + 0x24]
		movss dword ptr [esp + 0x30], xmm1
		mulss xmm0, dword ptr [esp + 0x30]
		movss xmm1, dword ptr [eax + 0x28]
		subss xmm1, xmm4
		subss xmm6, xmm0
		movss dword ptr [esp + 0x1c], xmm1
		movss dword ptr [esp + 0x2c], xmm6
		mov eax, dword ptr [esp + 0x2c]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0345
		movss xmm0, dword ptr [esi + 0x18]
		movaps xmm1, xmm6
		andps xmm1, xmmword ptr [absoluteMask]
		comiss xmm0, xmm1
		jae label_0345
		mulss xmm5, dword ptr [esp + 0x1c]
		movaps xmm0, xmm3
		mov eax, dword ptr [esp + 0x28]
		mulss xmm0, dword ptr [esp + 0x30]
		mulss xmm3, dword ptr [esp + 0x24]
		mulss xmm7, dword ptr [esp + 0x1c]
		subss xmm5, xmm0
		movss xmm0, dword ptr [eax]
		subss xmm3, xmm7
		divss xmm5, xmm6
		divss xmm3, xmm6
		mulss xmm0, xmm5
		movaps xmm6, xmm4
		movss dword ptr [esp + 0x30], xmm5
		mov eax, dword ptr [esp + 0x30]
		subss xmm6, xmm0
		and eax, 0x7f800000
		movaps xmm0, xmm2
		mulss xmm0, xmm3
		subss xmm6, xmm0
		cmp eax, 0x7f800000
		je label_0345
		movss dword ptr [esp + 0x30], xmm3
		mov eax, dword ptr [esp + 0x30]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0345
		movss dword ptr [esp + 0x30], xmm6
		mov eax, dword ptr [esp + 0x30]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0345
		mov eax, dword ptr [esp + 0x28]
		movaps xmm1, xmm5
		movss xmm7, dword ptr [eax + 0x64]
		mulss xmm1, dword ptr [eax + 0x60]
		movaps xmm0, xmm7
		mulss xmm0, xmm3
		addss xmm1, xmm0
		movss xmm0, dword ptr [eax + 0x68]
		addss xmm1, xmm6
		subss xmm0, xmm1
		movss dword ptr [esp + 0x30], xmm0
		mov eax, dword ptr [esp + 0x30]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0345
		andps xmm0, xmmword ptr [absoluteMask]
		comiss xmm0, dword ptr [esi + 0x1c]
		ja label_0345
		mov eax, dword ptr [esp + 0x28]
		movss xmm0, dword ptr [eax + 0x24]
		comiss xmm0, xmm2
		jbe label_02a0
		movss xmm4, dword ptr [eax + 0x28]
		movaps xmm2, xmm0
	label_02a0:
		movss xmm0, dword ptr [eax + 0x44]
		comiss xmm0, xmm2
		jbe label_02b2
		movss xmm4, dword ptr [eax + 0x48]
		movaps xmm2, xmm0
	label_02b2:
		comiss xmm7, xmm2
		jbe label_02bf
		movss xmm4, dword ptr [eax + 0x68]
		movaps xmm2, xmm7
	label_02bf:
		movss dword ptr [esp + 0x28], xmm2
		mov eax, dword ptr [esp + 0x28]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0345
		movss dword ptr [esp + 0x28], xmm4
		mov eax, dword ptr [esp + 0x28]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0345
		movss dword ptr [ecx + edx*8 + 0x10], xmm5
		movss dword ptr [ecx + edx*8 + 0x14], xmm3
		movss dword ptr [ecx + edx*8 + 0x18], xmm6
		movss dword ptr [ecx + edx*8 + 0x1c], xmm2
		movss dword ptr [ecx + edx*8 + 0x20], xmm4
		mov dword ptr [ecx + edx*8 + 0x24], 1
		mov eax, dword ptr [ecx + 0xc]
		bts eax, edi
		mov dword ptr [ecx + 0xc], eax
		mov edx, dword ptr [esi + 0x20]
		test edx, edx
		je label_0363
		mov ecx, dword ptr [esi + 0x24]
		test ecx, ecx
		je label_0363
		mov eax, dword ptr [esi + 0x30]
		test al, 1
		jne label_0363
		or eax, 1
		push ecx
		mov dword ptr [esi + 0x30], eax
		call edx
		pop edi
		mov eax, 1
		pop esi
		add esp, 0x18
		ret 0x10
	label_0345:
		mov ecx, dword ptr [esi + 0x20]
		test ecx, ecx
		je label_0363
		mov edx, dword ptr [esi + 0x2c]
		test edx, edx
		je label_0363
		mov eax, dword ptr [esi + 0x30]
		test al, 4
		jne label_0363
		or eax, 4
		push edx
		mov dword ptr [esi + 0x30], eax
		call ecx
	label_0363:
		pop edi
		mov eax, 1
		pop esi
		add esp, 0x18
		ret 0x10
	label_0370:
		mov eax, edx
		shr eax, 4
		movzx eax, al
		imul edi, eax, 0x88
		add edi, ecx
		mov dword ptr [esp + 0x24], edi
		cmp dword ptr [edi], edx
		jne label_0523
		mov eax, dword ptr [edi + 4]
		cmp eax, dword ptr [edx + 0x38]
		jne label_0523
		mov eax, dword ptr [edi + 8]
		cmp eax, dword ptr [edx + 0x3c]
		jne label_0523
		mov eax, dword ptr [edi + 0xc]
		and eax, 3
		cmp al, 3
		jne label_0523
		mov edi, dword ptr [esp + 0x28]
		xorps xmm3, xmm3
		movss xmm4, dword ptr [unitFloat]
		add edi, 4
		mov dword ptr [esp + 0x2c], 0
		mov dword ptr [esp + 0x1c], edi
	label_03d0:
		movss xmm2, dword ptr [edi + 4]
		movss dword ptr [esp + 0x18], xmm2
		mov eax, dword ptr [esp + 0x18]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0523
		comiss xmm3, xmm2
		ja label_0523
		comiss xmm2, xmm4
		ja label_0523
		mov edx, dword ptr [esp + 0x24]
		xor ecx, ecx
		add edx, 0x1c
		// Six-byte compiler alignment NOP (no data access).
		_emit 0x66
		_emit 0x0f
		_emit 0x1f
		_emit 0x44
		_emit 0x00
		_emit 0x00
	label_0410:
		mov edi, dword ptr [esp + 0x24]
		mov eax, 1
		mov esi, dword ptr [esp + 0x30]
		shl eax, cl
		test dword ptr [edi + 0xc], eax
		mov edi, dword ptr [esp + 0x1c]
		je label_047c
		cmp dword ptr [edx + 8], 0
		je label_047c
		movss xmm1, dword ptr [edi]
		comiss xmm1, dword ptr [edx]
		jb label_043e
		movss xmm0, dword ptr [edx + 4]
		jmp label_0456
	label_043e:
		movss xmm0, dword ptr [edi - 4]
		mulss xmm0, dword ptr [edx - 0xc]
		mulss xmm1, dword ptr [edx - 8]
		addss xmm0, xmm1
		addss xmm0, dword ptr [edx - 4]
	label_0456:
		movss dword ptr [esp + 0x18], xmm0
		mov eax, dword ptr [esp + 0x18]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0523
		subss xmm0, dword ptr [esi + 0x14]
		minss xmm0, xmm2
		movaps xmm2, xmm0
	label_047c:
		inc ecx
		add edx, 0x18
		cmp ecx, 5
		jl label_0410
		movss dword ptr [esp + 0x18], xmm2
		mov eax, dword ptr [esp + 0x18]
		and eax, 0x7f800000
		cmp eax, 0x7f800000
		je label_0523
		comiss xmm3, xmm2
		ja label_0523
		comiss xmm2, xmm4
		ja label_0523
		mov ecx, dword ptr [esp + 0x2c]
		add edi, 0x20
		mov dword ptr [esp + 0x1c], edi
		movss dword ptr [esp + ecx*4 + 8], xmm2
		inc ecx
		mov dword ptr [esp + 0x2c], ecx
		cmp ecx, 4
		jl label_03d0
		mov eax, dword ptr [esp + 0x28]
		movss xmm0, dword ptr [esp + 8]
		movss dword ptr [eax + 8], xmm0
		movss xmm0, dword ptr [esp + 0xc]
		movss dword ptr [eax + 0x28], xmm0
		movss xmm0, dword ptr [esp + 0x10]
		movss dword ptr [eax + 0x48], xmm0
		movss xmm0, dword ptr [esp + 0x14]
		movss dword ptr [eax + 0x68], xmm0
		mov edx, dword ptr [esi + 0x20]
		test edx, edx
		je label_0516
		mov ecx, dword ptr [esi + 0x28]
		test ecx, ecx
		je label_0516
		mov eax, dword ptr [esi + 0x30]
		test al, 2
		jne label_0516
		or eax, 2
		push ecx
		mov dword ptr [esi + 0x30], eax
		call edx
	label_0516:
		pop edi
		mov eax, 2
		pop esi
		add esp, 0x18
		ret 0x10
	label_0523:
		mov ecx, dword ptr [esi + 0x20]
		test ecx, ecx
		je label_0541
		mov edx, dword ptr [esi + 0x2c]
		test edx, edx
		je label_0541
		mov eax, dword ptr [esi + 0x30]
		test al, 4
		jne label_0541
		or eax, 4
		push edx
		mov dword ptr [esi + 0x30], eax
		call ecx
	label_0541:
		pop edi
		xor eax, eax
		pop esi
		add esp, 0x18
		ret 0x10
		// Historical zero padding before the 16-byte-aligned constant mask.
		_emit 0
		_emit 0
		_emit 0
		_emit 0
		_emit 0
	absoluteMask:
		_emit 0xff
		_emit 0xff
		_emit 0xff
		_emit 0x7f
		_emit 0xff
		_emit 0xff
		_emit 0xff
		_emit 0x7f
		_emit 0xff
		_emit 0xff
		_emit 0xff
		_emit 0x7f
		_emit 0xff
		_emit 0xff
		_emit 0xff
		_emit 0x7f
	unitFloat:
		_emit 0x00
		_emit 0x00
		_emit 0x80
		_emit 0x3f
	}
}
