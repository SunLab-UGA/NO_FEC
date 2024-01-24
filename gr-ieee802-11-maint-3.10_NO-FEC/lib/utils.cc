/*
 * Copyright (C) 2013 Bastian Bloessl <bloessl@ccs-labs.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "utils.h"

#include <math.h>
#include <cassert>
#include <cstring>

using gr::ieee802_11::BPSK_1_2;
using gr::ieee802_11::BPSK_3_4;
using gr::ieee802_11::QPSK_1_2;
using gr::ieee802_11::QPSK_3_4;
using gr::ieee802_11::QAM16_1_2;
using gr::ieee802_11::QAM16_3_4;
using gr::ieee802_11::QAM64_2_3;
using gr::ieee802_11::QAM64_3_4;

ofdm_param::ofdm_param(Encoding e)
{
    encoding = e;

    switch (e) {
    case BPSK_1_2:
        n_bpsc = 1; // number of coded bits per sub carrier
        n_cbps = 48; // number of coded bits per OFDM symbol
        n_dbps = 48; // number of data bits per OFDM symbol //was 24
        rate_field = 0x0D; // 0b00001101
        break;

    case BPSK_3_4:
        n_bpsc = 1;
        n_cbps = 48;
        n_dbps = 48; //36
        rate_field = 0x0F; // 0b00001111
        break;

    case QPSK_1_2:
        n_bpsc = 2;
        n_cbps = 96;
        n_dbps = 96; //48
        rate_field = 0x05; // 0b00000101
        break;

    case QPSK_3_4:
        n_bpsc = 2;
        n_cbps = 96;
        n_dbps = 96; //72
        rate_field = 0x07; // 0b00000111
        break;

    case QAM16_1_2:
        n_bpsc = 4;
        n_cbps = 192;
        n_dbps = 192; //96
        rate_field = 0x09; // 0b00001001
        break;

    case QAM16_3_4:
        n_bpsc = 4;
        n_cbps = 192;
        n_dbps = 192; //144
        rate_field = 0x0B; // 0b00001011
        break;

    case QAM64_2_3:
        n_bpsc = 6;
        n_cbps = 288;
        n_dbps = 288; //192
        rate_field = 0x01; // 0b00000001
        break;

    case QAM64_3_4:
        n_bpsc = 6;
        n_cbps = 288;
        n_dbps = 288; //216
        rate_field = 0x03; // 0b00000011
        break;
    defaut:
        assert(false);
        break;
    }
}


void ofdm_param::print()
{
    std::cout << "OFDM Parameters:" << std::endl;
    std::cout << "endcoding :" << encoding << std::endl;
    std::cout << "rate_field :" << (int)rate_field << std::endl; // rate field of the SIGNAL header
    std::cout << "n_bpsc :" << n_bpsc << std::endl; // number of coded bits per sub carrier
    std::cout << "n_cbps :" << n_cbps << std::endl; // number of coded bits per OFDM symbol
    std::cout << "n_dbps :" << n_dbps << std::endl; // number of data bits per OFDM symbol
}


frame_param::frame_param(ofdm_param& ofdm, int psdu_length)
{

    psdu_size = psdu_length;

    // number of symbols (17-11)
    n_sym = (int)ceil((16 + 8 * psdu_size + 6) / (double)ofdm.n_dbps);

    n_data_bits = n_sym * ofdm.n_dbps;

    // number of padding bits (17-13)
    n_pad = n_data_bits - (16 + 8 * psdu_size + 6);

    n_encoded_bits = n_sym * ofdm.n_cbps;
}
void frame_param::print()
{
    std::cout << "FRAME Parameters:" << std::endl;
    std::cout << "psdu_size: " << psdu_size << std::endl;
    std::cout << "n_sym: " << n_sym << std::endl;
    std::cout << "n_pad: " << n_pad << std::endl;
    std::cout << "n_encoded_bits: " << n_encoded_bits << std::endl;
    std::cout << "n_data_bits: " << n_data_bits << std::endl;
}


void scramble(const char* in, char* out, frame_param& frame, char initial_state)
// lsfr with polynomial x^6 + x^3 + 1
{

    int state = initial_state;
    int feedback;

    for (int i = 0; i < frame.n_data_bits; i++) {

        feedback = (!!(state & 64)) ^ (!!(state & 8));
        out[i] = feedback ^ in[i];
        state = ((state << 1) & 0x7e) | feedback;
    }
}


void reset_tail_bits(char* scrambled_data, frame_param& frame)
// reset the last 6 tail bytes to zero
{
    memset(scrambled_data + frame.n_data_bits - frame.n_pad - 6, 0, 6 * sizeof(char));
}


int ones(int n)
// count number of ones in binary representation of n
{
    int sum = 0;
    for (int i = 0; i < 8; i++) {
        if (n & (1 << i)) {
            sum++;
        }
    }
    return sum;
}


void convolutional_encoding(const char* in, char* out, frame_param& frame)
// convolutional encoding with 0155 and 0117 (octal), 0b0110_1101 and 0b0111_1111
{

    int state = 0;

    for (int i = 0; i < frame.n_data_bits; i++) {
        assert(in[i] == 0 || in[i] == 1);
        state = ((state << 1) & 0x7e) | in[i];
        out[i * 2] = ones(state & 0155) % 2;
        out[i * 2 + 1] = ones(state & 0117) % 2;
    }
}


void puncturing(const char* in, char* out, frame_param& frame, ofdm_param& ofdm)
{

    int mod;

    for (int i = 0; i < frame.n_data_bits * 2; i++) {
        switch (ofdm.encoding) {
        case BPSK_1_2:
        case QPSK_1_2:
        case QAM16_1_2:
            *out = in[i];
            out++;
            break;

        case QAM64_2_3:
            if (i % 4 != 3) {
                *out = in[i];
                out++;
            }
            break;

        case BPSK_3_4:
        case QPSK_3_4:
        case QAM16_3_4:
        case QAM64_3_4:
            mod = i % 6;
            if (!(mod == 3 || mod == 4)) {
                *out = in[i];
                out++;
            }
            break;
        defaut:
            assert(false);
            break;
        }
    }
}


void interleave(
    const char* in, char* out, frame_param& frame, ofdm_param& ofdm, bool reverse)
{

    int n_cbps = ofdm.n_cbps; // number of coded bits per OFDM symbol
    int first[MAX_BITS_PER_SYM];
    int second[MAX_BITS_PER_SYM];
    int s = std::max(ofdm.n_bpsc / 2, 1); // number of sub carriers per sub block

    for (int j = 0; j < n_cbps; j++) {
        first[j] = s * (j / s) + ((j + int(floor(16.0 * j / n_cbps))) % s); 
    }

    for (int i = 0; i < n_cbps; i++) {
        second[i] = 16 * i - (n_cbps - 1) * int(floor(16.0 * i / n_cbps)); // 16*i - floor(16*i/n_cbps)*(n_cbps-1)
    }

    for (int i = 0; i < frame.n_sym; i++) {
        for (int k = 0; k < n_cbps; k++) {
            if (reverse) {
                out[i * n_cbps + second[first[k]]] = in[i * n_cbps + k];
            } else {
                out[i * n_cbps + k] = in[i * n_cbps + second[first[k]]];
            }
        }
    }
}


void split_symbols(const char* in, char* out, frame_param& frame, ofdm_param& ofdm)
// split the interleaved data into OFDM symbols
{

    int symbols = frame.n_sym * 48;

    for (int i = 0; i < symbols; i++) {
        out[i] = 0;
        for (int k = 0; k < ofdm.n_bpsc; k++) {
            assert(*in == 1 || *in == 0);
            out[i] |= (*in << k);
            in++;
        }
    }
}


void generate_bits(const char* psdu, char* data_bits, frame_param& frame)
// generate the WIFI data field, adding service field and pad bits
{

    // first 16 bits are zero (SERVICE/DATA field)
    memset(data_bits, 0, 16); // set first 16 bits to zero
    data_bits += 16; // offset the pointer by length of SERVICE/DATA field

    for (int i = 0; i < frame.psdu_size; i++) { // copy the PSDU, i is byte index
        for (int b = 0; b < 8; b++) { // bit order is MSB first
            data_bits[i * 8 + b] = !!(psdu[i] & (1 << b)); // copy bit, ensure 0 or 1
        }
    }
}
