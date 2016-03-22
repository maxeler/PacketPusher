#define _GNU_SOURCE

#include <arpa/inet.h>
#include <netinet/in.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <err.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>


#include "MaxSLiCInterface.h"
//#include "MaxSLiCNetInterface.h"

extern max_file_t *PacketPusher_init();

struct packet_hdr {
	uint32_t sec;
	uint32_t nsec;
	uint32_t saved_len;
	uint32_t real_len;
};

int main(int argc, char *argv[]) {
	FILE *in;
	unsigned char *packetbuf;
	struct stat statbuf;
	char *filename;
	unsigned long filesize;
	size_t offset, bufsize, buf_offset;
	int be, started = 0, time_override = 0;
	uint32_t magic = 0;
	struct packet_hdr hdr;
	uint64_t prev_timestamp = 0;
	uint64_t frame_gap;

	if(argc < 2 || argc > 3) {
		fprintf(stderr, "Syntax: packetpush <pcap file> [<time in ns between packets>]\n");
		exit(1);
	}
	filename = argv[1];
	if(argc == 3) {
		frame_gap = atol(argv[2]);
		time_override = 1;
	}
	
	if(stat(filename, &statbuf)) {
		fprintf(stderr, "Failed to stat file %s\n", filename);
		exit(1);
	}
	filesize = statbuf.st_size;
	in = fopen(filename, "rb");
	if(!in) {
		fprintf(stderr, "Failed to open file %s\n", filename);
		exit(1);
	}
	
	offset = fread(&magic, 1, 4, in);
	if(magic == 0xa1b23c4d) {
		be = 0;
	} else if(magic == htonl(0xa1b23c4d)) {
		be = 1;
	} else {
		fprintf(stderr, "File %s not a valid pcap (or old format)\n", filename);
		exit(1);
	}
	fseek(in, 24, SEEK_SET);
	offset = 24;
	buf_offset = 0;
	bufsize = 0;
	packetbuf = NULL;
	
	while(offset < filesize) {
		uint32_t inlen, padding;
		uint64_t this_timestamp, outlen;
		offset += fread(&hdr, 1, 16, in);
		if(be) {
			hdr.sec = ntohl(hdr.sec);
			hdr.nsec = ntohl(hdr.nsec);
			hdr.saved_len = ntohl(hdr.saved_len);
			hdr.real_len = ntohl(hdr.real_len);
		}
		if(hdr.real_len < hdr.saved_len) {
			inlen = hdr.real_len;
			padding = hdr.saved_len - hdr.real_len;
		} else {
			inlen = hdr.saved_len;
			padding = 0;
		}
		outlen = (inlen+7) & ~7;
		while(bufsize < buf_offset + 16 + outlen) {
			bufsize += (filesize+15) & ~15;
			if(!(packetbuf = realloc(packetbuf, bufsize))) {
				fprintf(stderr, "Failed to allocate %lu bytes\n", bufsize);
				exit(1);
			}
		}
		this_timestamp = ((uint64_t) hdr.sec)*1e10 + ((uint64_t) hdr.nsec)*10;
		*((uint64_t *) (&packetbuf[buf_offset+8])) = inlen+16;
		if(started) {
			if(time_override) {
				*((uint64_t *) (&packetbuf[buf_offset])) = frame_gap*10;
			} else {
				*((uint64_t *) (&packetbuf[buf_offset])) = this_timestamp - prev_timestamp;
			}
		} else {
			*((uint64_t *) (&packetbuf[buf_offset])) = 0;
			started = 1;
		}
		prev_timestamp = this_timestamp;
		offset += fread(&packetbuf[buf_offset+16], 1, inlen, in);
		fseek(in, padding, SEEK_CUR);
		offset += padding;
		buf_offset += 16 + outlen;
	}
	
	fclose(in);

	max_file_t *maxfile = PacketPusher_init();
	max_engine_t * engine = max_load(maxfile, "*");


	max_config_set_bool(MAX_CONFIG_PRINTF_TO_STDOUT, true);

	max_actions_t *action = max_actions_init(maxfile, NULL);
	max_queue_input(action, "fromCPU", packetbuf, (buf_offset+15) & ~15);
	max_run(engine, action);

	printf("Sending finished\n");
	getchar();

	max_unload(engine);
	max_file_free(maxfile);

	return 0;
}
